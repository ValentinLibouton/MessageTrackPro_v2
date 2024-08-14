import sqlite3
from database.sql_request import SQLRequest
from utils.string_cleaner import StringCleaner


class EmailDatabase:
    def __init__(self, db_name='database.db', sql_file='database/database.sql', string_cleaner=None, sql_requests=None):
        self.string_cleaner = string_cleaner if string_cleaner else StringCleaner()
        self.db_name = db_name
        self.sql_file = sql_file
        self.sql_requests = sql_requests if sql_requests else SQLRequest()
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        with open(self.sql_file, 'r') as f:
            sql = f.read()
        c.executescript(sql)
        conn.commit()
        conn.close()


    def insert_contact(self, first_name, last_name, return_existing_id=False):
        first_name = self.string_cleaner.to_lower_and_strip(first_name)
        last_name = self.string_cleaner.to_lower_and_strip(last_name)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Contacts',
                                               columns=['first_name', 'last_name']), (first_name, last_name))
            contact_id = c.lastrowid
            if contact_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table='Contacts',
                                                                    columns=['first_name', 'last_name']), (first_name, last_name))
                contact_id = c.fetchone()[0]
            return contact_id

    def insert_alias(self, alias, return_existing_id=False):
        alias = self.string_cleaner.to_lower_and_strip(alias)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Alias',
                                               columns=['alias']), (alias,))
            alias_id = c.lastrowid
            if alias_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table='Alias',
                                                                    columns=['alias']), (alias,))
                alias_id = c.fetchone()[0]
            return alias_id

    def insert_email_address(self, email_address, return_existing_id=False):
        email_address = self.string_cleaner.to_lower_and_strip(email_address)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='EmailAddresses',
                                               columns=['email_address']), (email_address,))
            address_id = c.lastrowid
            if address_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table='EmailAddresses',
                                                                    columns=['email_address']), (email_address,))
                address_id = c.fetchone()[0]
            return address_id

    def insert_email(self, id, filepath, filename, subject, body, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Emails',
                                               columns=['id', 'filepath', 'filename', 'subject', 'body'])
                      , (id, filepath, filename, subject, body))
            conn.commit()
            return id

    def insert_date(self, date, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Date',
                                               columns=['date']), (date,))
            date_id = c.lastrowid
            if date_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table='Date',
                                                                    columns=['date']), (date,))
                date_id = c.fetchone()[0]
            return date_id

    def insert_timestamp(self, timestamp, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Timestamp',
                                               columns=['timestamp']), (timestamp,))
            timestamp_id = c.lastrowid
            if timestamp_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table='Timestamp',
                                                                    columns=['timestamp']), (timestamp,))
                timestamp_id = c.fetchone()[0]
            return timestamp_id

    def insert_attachment(self, id, filename, content, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Attachments',
                                               columns=['id', 'filename', 'content'])
                      , (id, filename, content))
            conn.commit()
            return id

    def link(self, table, col_name_1, col_name_2, value_1, value_2):
        """Only 'value_2' can be of type (list, tuple, set) in addition to being of type int or str"""
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
