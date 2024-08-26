import sqlite3
from database.sql_request import SQLRequest
from utils.string_cleaner import StringCleaner
from utils.logging_setup import log_email_database
from config.db_constants import DBConstants


class EmailDatabase:
    def __init__(self, db_name=DBConstants.db_name, sql_file=DBConstants.sql_name, string_cleaner=None, sql_requests=None):
        self.string_cleaner = string_cleaner if string_cleaner else StringCleaner()
        self.db_name = db_name
        self.sql_file = sql_file
        self.sql_requests = sql_requests if sql_requests else SQLRequest()
        self._create_tables()

    def _create_tables(self):
        log_email_database.info(f"Func: _create_tables, database creation")
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        with open(self.sql_file, 'r') as f:
            sql = f.read()
        c.executescript(sql)
        conn.commit()
        conn.close()


    def insert_contact(self, first_name, last_name, return_existing_id=False):
        #log_email_database.info(f"Func: insert_contact")
        first_name = self.string_cleaner.to_lower_and_strip(first_name)
        last_name = self.string_cleaner.to_lower_and_strip(last_name)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table=DBConstants.CONTACTS_TABLE,
                                               columns=DBConstants.CONTACTS_COLUMNS)
                      , (first_name, last_name))
            contact_id = c.lastrowid
            if contact_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table=DBConstants.CONTACTS_TABLE,
                                                                    columns=DBConstants.CONTACTS_COLUMNS),
                          (first_name, last_name))
                contact_id = c.fetchone()[0]
            return contact_id

    def insert_alias(self, alias, return_existing_id=False):
        #log_email_database.info(f"Func: insert_alias")
        alias = self.string_cleaner.to_lower_and_strip(alias)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table=DBConstants.ALIAS_TABLE,
                                               columns=DBConstants.ALIAS_COLUMNS), (alias,))
            alias_id = c.lastrowid
            if alias_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table=DBConstants.ALIAS_TABLE,
                                                                    columns=DBConstants.ALIAS_COLUMNS),
                          (alias,))
                alias_id = c.fetchone()[0]
            return alias_id

    def insert_email_address(self, email_address, return_existing_id=False):
        #log_email_database.info(f"Func: insert_email_address")
        email_address = self.string_cleaner.to_lower_and_strip(email_address)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table=DBConstants.EMAIL_ADDRESSES_TABLE,
                                               columns=DBConstants.EMAIL_ADDRESSES_COLUMNS)
                      , (email_address,))
            address_id = c.lastrowid
            if address_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table=DBConstants.EMAIL_ADDRESSES_TABLE,
                                                                    columns=DBConstants.EMAIL_ADDRESSES_COLUMNS)
                          , (email_address,))
                address_id = c.fetchone()[0]
            return address_id

    def insert_email(self, id, filepath, filename, subject, body, return_existing_id=False):
        log_email_database.info(f"Func: insert_email")
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table=DBConstants.EMAILS_TABLE,
                                               columns=DBConstants.EMAILS_COLUMNS)
                      , (id, filepath, filename, subject, body))
            conn.commit()
            return id

    def insert_date(self, date, return_existing_id=False):
        #log_email_database.info(f"Func: insert_date")
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table=DBConstants.DATE_TABLE,
                                               columns=DBConstants.DATE_COLUMNS), (date,))
            date_id = c.lastrowid
            if date_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table=DBConstants.DATE_TABLE,
                                                                    columns=DBConstants.DATE_COLUMNS)
                          , (date,))
                row = c.fetchone()
                if row is not None:
                    date_id = row[0]
                else:
                    return None
            return date_id

    def insert_timestamp(self, timestamp, return_existing_id=False):
        #log_email_database.info(f"Func: insert_timestamp")
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table=DBConstants.TIMESTAMP_TABLE,
                                               columns=DBConstants.TIMESTAMP_COLUMNS), (timestamp,))
            timestamp_id = c.lastrowid
            if timestamp_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table=DBConstants.TIMESTAMP_TABLE,
                                                                    columns=DBConstants.TIMESTAMP_COLUMNS)
                          , (timestamp,))
                row = c.fetchone()
                if row is not None:
                    timestamp_id = row[0]
                else:
                    return None
            return timestamp_id


    def insert_attachment(self, id, filename, content, extracted_text, return_existing_id=False):
        log_email_database.info(f"Func: insert_attachment")
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table=DBConstants.ATTACHMENTS_TABLE,
                                               columns=DBConstants.ATTACHMENTS_COLUMNS)
                      , (id, filename, content, extracted_text))
            conn.commit()
            return id

    def link(self, table, col_name_1, col_name_2, value_1, value_2):
        """Only 'value_2' can be of type (list, tuple, set) in addition to being of type int or str"""
        #log_email_database.info(f"Func: link, Table: {table}")
        request = self.sql_requests.link(table=table, col_name_1=col_name_1, col_name_2=col_name_2)
        if isinstance(value_2, (list, tuple, set)):
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.executemany(request, [(value_1, value) for value in value_2])
                conn.commit()
        else:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute(request, (value_1, value_2))
                conn.commit()
