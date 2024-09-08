# database_retriever.py
# Interfaces
from database.idatabase_retriever import IDatabaseRetriever

# Constants
from config.db_constants import DBConstants, DatabaseRetrieverConstants
from config.sql_constants import *

# Personal libraries
from utils.date_transformer import DateTransformer
from utils.string_cleaner import StringCleaner

# Libraries
from abc import abstractmethod
import sqlite3
from typing import Self


class DatabaseRetriever(IDatabaseRetriever):
    def __init__(self, db_name: str = DBConstants.DB_NAME, contacts: list = [], aliases: list = [],
                 addresses: list = [], start_date: str = "", end_date: str = "", words: list = [],
                 words_localization: list = [], word_operator: str = 'OR', attachment_types: list = []):
        """
        : contacts: filtering on specific contacts
        : aliases: filtering on specific aliases
        : addresses: filtering on specific email addresses
        : start_date: filtering on start date, ex. str(YYYY-MM-DD hh:mm:ss)
        : end_date: filtering on end date,ex. str(YYYY-MM-DD hh:mm:ss)
        : words: list of words to find
        :words_localization: list of words localization ['everywhere', 'contact', 'alias', 'address',
                                'subject', 'body', 'attachment_name', 'attachment']
        :word_operator: "AND" or "OR"
        :attachment_types: filtering on attachment types

        """
        # region args
        self.db_name = db_name
        self.contacts = contacts
        self.aliases = aliases
        self.addresses = addresses
        self.start_date = start_date
        self.end_date = end_date
        self.words = words
        self.words_localization = words_localization
        self.word_operator = word_operator
        self.attachment_types = attachment_types
        # endregion
        # region constants
        self.valid_localizations = DatabaseRetrieverConstants.KEYWORD_SEARCH_FIELDS  # todo
        self.everywhere = DatabaseRetrieverConstants.EVERYWHERE_LOCALISATION
        # endregion
        # region initialization
        self.words_localization = self.configure_localization(everywhere=self.everywhere,
                                                              words_localization=self.words_localization,
                                                              valid_localizations=self.valid_localizations)
        self.__start_timestamp, self.__end_timestamp = self.date_settings(start_date=self.start_date,
                                                                          end_date=self.end_date)
        # endregion

        self.sc = StringCleaner()
        self.join_clauses = []
        self.where_clauses = set()
        self.where_and_clauses = set()  # mandatory clauses (AND) ex. dates
        self.order_by_clause = ""
        self.limit_clause = ""
        self.request = ""

    def validate_arguments(self) -> None:
        for arg in [self.db_name, self.start_date, self.end_date, self.word_operator]:
            if not isinstance(arg, str):
                raise TypeError(f'{arg} must be a string')

        for arg in [self.contacts, self.aliases, self.addresses, self.words, self.words_localization,
                    self.attachment_types]:
            if not isinstance(arg, list):
                raise TypeError(f'{arg} must be a list')

        self.word_operator = self.word_operator.upper()
        if self.word_operator not in ["AND", "OR"]:
            raise TypeError(f'word operator must be OR or AND, value: {self.word_operator}')

    @abstractmethod
    def configure_localization(self, everywhere, words_localization, valid_localizations) -> list:
        if words_localization == []:
            return words_localization
        elif everywhere in words_localization:
            words_localization = [everywhere]
        else:
            for localization in words_localization:
                if localization not in valid_localizations:
                    raise ValueError(
                        f"{localization} is not a valid words localization, valid values are: {valid_localizations}")
        return words_localization

    @abstractmethod
    def date_settings(self, start_date: str, end_date: str) -> tuple[int, int]:
        dt = DateTransformer()
        start_date = start_date if start_date else 0
        end_date = end_date if end_date else None
        return dt.convert_to_timestamp(start_date), dt.convert_to_timestamp(end_date)

    def select(self) -> Self:
        self.request = f"""SELECT DISTINCT {E_ID} FROM {TABLE_EMAILS} {ALIAS_EMAILS}"""
        return self

    def add_join(self, join_clause: str) -> None:
        if join_clause not in self.join_clauses:
            if len(self.join_clauses) == 0:
                join_clause = join_clause.replace('LEFT JOIN', 'JOIN', 1)
            self.request += f" {join_clause}"
            self.join_clauses.append(join_clause)

    def add_where(self, condition: str) -> Self:
        self.where_clauses.add(condition)
        return self

    def add_where_and(self, condition: str) -> Self:
        self.where_and_clauses.add(f"({condition})")
        return self

    def add_order_by(self, columns: list, ascending=True) -> None:
        order = "ASC" if ascending else "DESC"
        self.order_by_clause += f"ORDER BY {', '.join(columns)} {order}"

    def add_limit(self, limit: int) -> Self:
        self.limit_clause = f"LIMIT {limit}"
        return self

    def build_query(self) -> str:
        self.select()
        if self.join_clauses:
            self.request += " " + " ".join(self.join_clauses)

        if self.where_and_clauses:
            self.request += " WHERE " + f" AND ".join(self.where_and_clauses)

        if self.where_clauses:
            if self.where_and_clauses:
                self.request += f" AND "
            else:
                self.request += " WHERE "
            self.request += f" {self.word_operator} ".join(self.where_clauses)

        if self.order_by_clause:
            # ToDo: Not implemented
            self.request += " " + self.order_by_clause

        if self.limit_clause:
            # ToDo: Not implemented
            self.request += " " + self.limit_clause
        return self.request

    def join(self) -> Self:
        if self.everywhere in self.words_localization and self.words:
            self._join_email_addresses()
            self._join_contacts()
            self._join_aliases()
            self._join_dates()
            self._join_attachments()
        if self.contacts or (DatabaseRetrieverConstants.CONTACT in self.words_localization and self.words):
            self._join_email_addresses()
            self._join_contacts()
        if self.aliases or (DatabaseRetrieverConstants.ALIAS in self.words_localization and self.words):
            self._join_email_addresses()
            self._join_contacts()
            self._join_aliases()
        if self.addresses or (DatabaseRetrieverConstants.ADDRESS in self.words_localization and self.words):
            self._join_email_addresses()
        if self.start_date or self.end_date:
            self._join_dates()
        if self.attachment_types or (
                DatabaseRetrieverConstants.ATTACHMENT in self.words_localization and self.words) or (
                DatabaseRetrieverConstants.ATTACHMENT_NAME in self.words_localization and self.words):
            self._join_attachments()
        return self

    def _join_email_addresses(self) -> None:
        self.add_join(f"LEFT JOIN {TABLE_EMAIL_FROM} {ALIAS_EMAIL_FROM} ON {E_ID} = {EF_EMAIL_ID}")
        self.add_join(f"LEFT JOIN {TABLE_EMAIL_TO} {ALIAS_EMAIL_TO} ON {E_ID} = {ET_EMAIL_ID}")
        self.add_join(f"LEFT JOIN {TABLE_EMAIL_CC} {ALIAS_EMAIL_CC} ON {E_ID} = {EC_EMAIL_ID}")
        self.add_join(f"LEFT JOIN {TABLE_EMAIL_BCC} {ALIAS_EMAIL_BCC} ON {E_ID} = {EB_EMAIL_ID}")

        self.add_join(
            f"LEFT JOIN {TABLE_EMAIL_ADDRESSES} {ALIAS_EMAIL_ADDRESSES_FROM} ON {EA1_ID} = {EF_EMAIL_ADDRESS_ID}")
        self.add_join(
            f"LEFT JOIN {TABLE_EMAIL_ADDRESSES} {ALIAS_EMAIL_ADDRESSES_TO} ON {EA2_ID} = {ET_EMAIL_ADDRESS_ID}")
        self.add_join(
            f"LEFT JOIN {TABLE_EMAIL_ADDRESSES} {ALIAS_EMAIL_ADDRESSES_CC} ON {EA3_ID} = {EC_EMAIL_ADDRESS_ID}")
        self.add_join(
            f"LEFT JOIN {TABLE_EMAIL_ADDRESSES} {ALIAS_EMAIL_ADDRESSES_BCC} ON {EA4_ID} = {EB_EMAIL_ADDRESS_ID}")

    def _join_contacts(self) -> None:
        self.add_join(
            f"LEFT JOIN {TABLE_CONTACTS_EMAIL_ADDRESSES} {ALIAS_CONTACTS_EMAIL_ADDRESSES_FROM} ON {EA1_ID} = {CEA1_EMAIL_ADDRESS_ID}")
        self.add_join(
            f"LEFT JOIN {TABLE_CONTACTS_EMAIL_ADDRESSES} {ALIAS_CONTACTS_EMAIL_ADDRESSES_TO} ON {EA2_ID} = {CEA2_EMAIL_ADDRESS_ID}")
        self.add_join(
            f"LEFT JOIN {TABLE_CONTACTS_EMAIL_ADDRESSES} {ALIAS_CONTACTS_EMAIL_ADDRESSES_CC} ON {EA3_ID} = {CEA3_EMAIL_ADDRESS_ID}")
        self.add_join(
            f"LEFT JOIN {TABLE_CONTACTS_EMAIL_ADDRESSES} {ALIAS_CONTACTS_EMAIL_ADDRESSES_BCC} ON {EA4_ID} = {CEA4_EMAIL_ADDRESS_ID}")

        self.add_join(f"LEFT JOIN {TABLE_CONTACTS} {ALIAS_CONTACTS_FROM} ON {CEA1_CONTACT_ID} = {C1_ID}")
        self.add_join(f"LEFT JOIN {TABLE_CONTACTS} {ALIAS_CONTACTS_TO} ON {CEA2_CONTACT_ID} = {C2_ID}")
        self.add_join(f"LEFT JOIN {TABLE_CONTACTS} {ALIAS_CONTACTS_CC} ON {CEA3_CONTACT_ID} = {C3_ID}")
        self.add_join(f"LEFT JOIN {TABLE_CONTACTS} {ALIAS_CONTACTS_BCC} ON {CEA4_CONTACT_ID} = {C4_ID}")

    def _join_aliases(self) -> None:
        self.add_join(f"LEFT JOIN {TABLE_CONTACTS_ALIAS} {ALIAS_CONTACTS_ALIAS_FROM} ON {C1_ID} = {CA1_CONTACT_ID}")
        self.add_join(f"LEFT JOIN {TABLE_CONTACTS_ALIAS} {ALIAS_CONTACTS_ALIAS_TO} ON {C2_ID} = {CA2_CONTACT_ID}")
        self.add_join(f"LEFT JOIN {TABLE_CONTACTS_ALIAS} {ALIAS_CONTACTS_ALIAS_CC} ON {C3_ID} = {CA3_CONTACT_ID}")
        self.add_join(f"LEFT JOIN {TABLE_CONTACTS_ALIAS} {ALIAS_CONTACTS_ALIAS_BCC} ON {C4_ID} = {CA4_CONTACT_ID}")

        self.add_join(f"LEFT JOIN {TABLE_ALIAS} {ALIAS_ALIAS_FROM} ON {CA1_ALIAS_ID} = {A1_ID}")
        self.add_join(f"LEFT JOIN {TABLE_ALIAS} {ALIAS_ALIAS_TO} ON {CA2_ALIAS_ID} = {A2_ID}")
        self.add_join(f"LEFT JOIN {TABLE_ALIAS} {ALIAS_ALIAS_CC} ON {CA3_ALIAS_ID} = {A3_ID}")
        self.add_join(f"LEFT JOIN {TABLE_ALIAS} {ALIAS_ALIAS_BCC} ON {CA4_ALIAS_ID} = {A4_ID}")

    def _join_dates(self) -> None:
        self.add_join(f"LEFT JOIN {TABLE_EMAIL_TIMESTAMP} {ALIAS_EMAIL_TIMESTAMP} ON {E_ID} = {ETI_EMAIL_ID}")
        self.add_join(f"LEFT JOIN {TABLE_TIMESTAMP} {ALIAS_TIMESTAMP} ON {ETI_TIMESTAMP_ID} = {TS_ID}")

    def _join_attachments(self) -> None:
        self.add_join(f"LEFT JOIN {TABLE_EMAIL_ATTACHMENTS} {ALIAS_EMAIL_ATTACHMENTS} ON {E_ID} = {EA_EMAIL_ID}")
        self.add_join(f"LEFT JOIN {TABLE_ATTACHMENTS} {ALIAS_ATTACHMENTS} ON {EA_ATTACHMENT_ID} = {A_ID}")

    def where(self) -> Self:
        self._where_date()
        self._where_contacts()
        self._where_aliases()
        self._where_addresses()
        self._where_attachments_types()
        self._where_words()
        return self

    def _where_date(self) -> None:
        date_conditions = []
        if self.start_date and self.end_date:
            date_conditions.append(f"{TS_TIMESTAMP} BETWEEN '{self.__start_timestamp}' AND '{self.__end_timestamp}'")
        elif self.start_date:
            date_conditions.append(f"{TS_TIMESTAMP} >= '{self.__start_timestamp}'")
        elif self.end_date:
            date_conditions.append(f"{TS_TIMESTAMP} <= '{self.__end_timestamp}'")
        if date_conditions:
            self.add_where_and(condition=" AND ".join(date_conditions))

    def _where_contacts(self) -> None:
        if self.contacts:
            FIRST_NAMES = [C1_FIRST_NAME, C2_FIRST_NAME, C3_FIRST_NAME, C4_FIRST_NAME]
            LAST_NAMES = [C1_LAST_NAME, C2_LAST_NAME, C3_LAST_NAME, C4_LAST_NAME]
            contact_conditions = " OR ".join(
                [f"LOWER({first}) = LOWER('{first_name}') AND LOWER({last}) = LOWER('{last_name}')"
                 for first_name, last_name in self.contacts for first, last in zip(FIRST_NAMES, LAST_NAMES)])
            self.add_where(f"({contact_conditions})")

    def _where_aliases(self) -> None:
        if self.aliases:
            ALIASES = [A1_ALIAS, A2_ALIAS, A3_ALIAS, A4_ALIAS]
            alias_conditions = " OR ".join(
                [f"LOWER({alias}) = LOWER('{request_alias}')" for request_alias in self.aliases for alias in ALIASES])
            self.add_where(f"({alias_conditions})")

    def _where_addresses(self) -> None:
        if self.addresses:
            EMAIL_ADDRESSES = [EA1_EMAIL_ADDRESS, EA2_EMAIL_ADDRESS, EA3_EMAIL_ADDRESS, EA4_EMAIL_ADDRESS]
            address_conditions = " OR ".join(
                [f"LOWER({email_address}) = LOWER('{address}')" for address in self.addresses for email_address in
                 EMAIL_ADDRESSES])
            self.add_where(f"({address_conditions})")

    def _where_attachments_types(self) -> None:
        if self.attachment_types:
            attachment_conditions = " OR ".join(
                [f"LOWER({A_FILENAME}) LIKE '%.{file_type.lower()}'" for file_type in self.attachment_types]
            )
            self.add_where(f"({attachment_conditions})")

    def _where_words(self) -> None:
        if self.words:
            word_conditions = []
            added_conditions = set()

            for word in self.words:
                word = word.lower()
                conditions = []

                if DatabaseRetrieverConstants.CONTACT in self.localizations:
                    FIRST_NAMES = [C1_FIRST_NAME, C2_FIRST_NAME, C3_FIRST_NAME, C4_FIRST_NAME]
                    LAST_NAMES = [C1_LAST_NAME, C2_LAST_NAME, C3_LAST_NAME, C4_LAST_NAME]
                    conditions.extend(
                        [f"LOWER({first_name}) LIKE '%{word}%' OR LOWER({last_name}) LIKE '%{word}%'" for
                         first_name, last_name in zip(FIRST_NAMES, LAST_NAMES)])

                if DatabaseRetrieverConstants.ALIAS in self.localizations:
                    ALIASES = [A1_ALIAS, A2_ALIAS, A3_ALIAS, A4_ALIAS]
                    conditions.extend([f"LOWER({alias}) LIKE '%{word}%'" for alias in ALIASES])

                if DatabaseRetrieverConstants.ADDRESS in self.localizations:
                    EMAIL_ADDRESSES = [EA1_EMAIL_ADDRESS, EA2_EMAIL_ADDRESS, EA3_EMAIL_ADDRESS, EA4_EMAIL_ADDRESS]
                    conditions.extend([f"LOWER({email_address}) LIKE '%{word}%'" for email_address in EMAIL_ADDRESSES])

                if DatabaseRetrieverConstants.SUBJECT in self.localizations:
                    conditions.append(f"LOWER({E_SUBJECT}) LIKE '%{word}%'")

                if DatabaseRetrieverConstants.BODY in self.localizations:
                    conditions.append(f"LOWER({E_BODY}) LIKE '%{word}%'")

                if DatabaseRetrieverConstants.ATTACHMENT_NAME in self.localizations:
                    conditions.append(f"LOWER({A_FILENAME}) LIKE '%{word}%'")

                if DatabaseRetrieverConstants.ATTACHMENT in self.localizations:
                    # ToDo: I need to develop a class which, depending on the type of extension,
                    #  will try to retrieve the text from EmailParser and add a column to the db to display the extracted text.
                    conditions.append(f"LOWER({A_EXTRACTED_TEXT}) LIKE '%{word}%'")

                if conditions:
                    # word_conditions.append(f"({' OR '.join(conditions)})")
                    combined_condition = f"({' OR '.join(conditions)})"

                    if combined_condition not in added_conditions:
                        word_conditions.append(combined_condition)
                        added_conditions.add(combined_condition)

            if word_conditions:
                self.add_where(f" {self.word_operator} ".join(word_conditions))

    def execute(self, params=None) -> list:
        query = self.build_query()
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(query, params or [])
            results = c.fetchall()
        return results

    def show_query(self) -> str:
        return self.build_query()
