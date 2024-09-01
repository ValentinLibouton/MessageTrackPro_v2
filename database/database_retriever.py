from abc import abstractmethod
import sqlite3
from typing import Self, Tuple
from database.sql_request import SQLRequest
from utils.date_transformer import DateTransformer
from config.db_constants import DBConstants, DatabaseRetrieverConstants
from utils.string_cleaner import StringCleaner


class DatabaseRetriever:
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
        # region objects
        self.sc = StringCleaner()

        self.join_clauses = []
        self.where_clauses = set()
        self.where_and_clauses = set()  # mandatory clauses (AND) ex. dates
        self.order_by_clause = ""
        self.limit_clause = ""
        self.request = ""

    def validate_arguments(self):
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
    def configure_localization(self, everywhere, words_localization, valid_localizations):
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
    def date_settings(self, start_date, end_date) -> tuple[int, int]:
        dt = DateTransformer()
        start_date = start_date if start_date else 0
        end_date = end_date if end_date else None
        return dt.convert_to_timestamp(start_date), dt.convert_to_timestamp(end_date)

    def select(self) -> Self:
        self.request = f"""SELECT DISTINCT e.id FROM Emails e"""
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
        # Todo arrivé ici. Je dois adapter la suite ci-dessous
        if self.params.get('start_date') or self.params.get('end_date'):
            self._join_dates()

        if (self.params.get('attachment_types')
                or ('attachment' in self.params.get('words_localization', []) and self.params.get('words', []))
                or ('attachment_name' in self.params.get('words_localization', []) and self.params.get('words', []))):
            self._join_attachments()

        return self

    def _join_email_addresses(self):
        self.add_join("LEFT JOIN Email_From ef ON e.id = ef.email_id")
        self.add_join("LEFT JOIN Email_To et ON e.id = et.email_id")
        self.add_join("LEFT JOIN Email_Cc ec ON e.id = ec.email_id")
        self.add_join("LEFT JOIN Email_Bcc eb ON e.id = eb.email_id")

        self.add_join("LEFT JOIN EmailAddresses ea1 ON ea1.id = ef.email_address_id")
        self.add_join("LEFT JOIN EmailAddresses ea2 ON ea2.id = et.email_address_id")
        self.add_join("LEFT JOIN EmailAddresses ea3 ON ea3.id = ec.email_address_id")
        self.add_join("LEFT JOIN EmailAddresses ea4 ON ea4.id = eb.email_address_id")

    def _join_contacts(self):
        [self.add_join(f"LEFT JOIN Contacts_EmailAddresses cea{i} ON ea{i}.id = cea{i}.email_address_id") for i in
         range(1, 5)]
        [self.add_join(f"LEFT JOIN Contacts c{i} ON cea{i}.contact_id = c{i}.id") for i in range(1, 5)]

    def _join_aliases(self):
        [self.add_join(f"LEFT JOIN Contacts_Alias ca{i} ON c{i}.id = ca{i}.contact_id") for i in range(1, 5)]
        [self.add_join(f"LEFT JOIN Alias a{i} ON ca{i}.alias_id = a{i}.id") for i in range(1, 5)]

    def _join_dates(self):
        # self.add_join("LEFT JOIN Email_Date ed ON e.id = ed.email_id")
        # self.add_join("LEFT JOIN Date d ON ed.date_id = d.id")
        self.add_join("LEFT JOIN Email_Timestamp eti ON e.id = eti.email_id")
        self.add_join("LEFT JOIN Timestamp ts ON eti.timestamp_id = ts.id")

    def _join_attachments(self):
        self.add_join("LEFT JOIN Email_Attachments ea ON e.id = ea.email_id")
        self.add_join("LEFT JOIN Attachments a ON ea.attachment_id = a.id")

    def where(self):
        self._where_date()
        self._where_contacts()
        self._where_aliases()
        self._where_addresses()
        self._where_attachments_types()
        self._where_words()
        return self

    def _where_date(self):
        date_conditions = []
        if self.params.get('start_date') and self.params.get('end_date'):
            date_conditions.append(f"ts.timestamp BETWEEN '{self.start_timestamp}' AND '{self.end_timestamp}'")
        elif self.params.get('start_date'):
            date_conditions.append(f"ts.timestamp >= '{self.start_timestamp}'")
        elif self.params.get('end_date'):
            date_conditions.append(f"ts.timestamp <= '{self.end_timestamp}'")
        if date_conditions:
            self.add_where_and(condition=" AND ".join(date_conditions))

    def _where_contacts(self):
        if self.params.get('contacts'):
            contact_conditions = " OR ".join(
                [f"LOWER(c{i}.first_name) = LOWER('{first_name}') AND LOWER(c{i}.last_name) = LOWER('{last_name}')"
                 for first_name, last_name in self.params['contacts'] for i in range(1, 5)])
            self.add_where(f"({contact_conditions})")

    def _where_aliases(self):
        if self.params.get('aliases'):
            alias_conditions = " OR ".join(
                [f"LOWER(a{i}.alias) = LOWER('{alias}')" for alias in self.params['aliases'] for i in range(1, 5)])
            self.add_where(f"({alias_conditions})")

    def _where_addresses(self):
        if self.params.get('addresses'):
            address_conditions = " OR ".join(
                [f"LOWER(ea{i}.email_address) = LOWER('{address}')" for address in self.params['addresses'] for i in
                 range(1, 5)])
            self.add_where(f"({address_conditions})")

    def _where_attachments_types(self):
        if self.params.get('attachments_type'):
            attachment_conditions = " OR ".join(
                [f"LOWER(a.filename) LIKE '%.{file_type.lower()}'" for file_type in self.params['attachment_types']]
            )
            self.add_where(f"({attachment_conditions})")

    def _where_words(self):
        if self.params.get('words'):
            word_conditions = []
            added_conditions = set()
            if "everywhere" in self.params.get('words_localization', []):
                localizations = self.valid_localizations[1:]
            else:
                localizations = self.params.get('words_localization', [])

            for word in self.params['words']:
                word = word.lower()
                conditions = []

                if "contact" in localizations:
                    conditions.extend(
                        [f"LOWER(c{i}.first_name) LIKE '%{word}%' OR LOWER(c{i}.last_name) LIKE '%{word}%'" for i in
                         range(1, 5)])

                if "alias" in localizations:
                    conditions.extend([f"LOWER(a{i}.alias) LIKE '%{word}%'" for i in range(1, 5)])

                if "address" in localizations:
                    conditions.extend([f"LOWER(ea{i}.email_address) LIKE '%{word}%'" for i in range(1, 5)])

                if "subject" in localizations:
                    conditions.append(f"LOWER(e.subject) LIKE '%{word}%'")

                if "body" in localizations:
                    conditions.append(f"LOWER(e.body) LIKE '%{word}%'")

                if "attachment_name" in localizations:
                    conditions.append(f"LOWER(a.filename) LIKE '%{word}%'")

                if "attachment" in localizations:
                    # ToDo: I need to develop a class which, depending on the type of extension,
                    #  will try to retrieve the text from EmailParser and add a column to the db to display the extracted text.
                    conditions.append(f"LOWER(a.extracted_text) LIKE '%{word}%'")

                if conditions:
                    # word_conditions.append(f"({' OR '.join(conditions)})")
                    combined_condition = f"({' OR '.join(conditions)})"

                    if combined_condition not in added_conditions:
                        word_conditions.append(combined_condition)
                        added_conditions.add(combined_condition)

            if word_conditions:
                self.add_where(f" {self.word_operator} ".join(word_conditions))

    def execute(self, params=None):
        query = self.build_query()
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(query, params or [])
            results = c.fetchall()
        return results

    def show_query(self):
        return self.build_query()
