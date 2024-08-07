import sqlite3
from sql_request import SQLRequest
from utils.string_cleaner import StringCleaner


class EmailDatabase:
    def __init__(self, data: dict, db_name='database.db', sql_file='database.sql', string_cleaner=None, sql_requests=None):
        self.string_cleaner = string_cleaner if string_cleaner else StringCleaner()
        self.data = data
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
        first_name = self.string_cleaner.to_lower_and_trim(first_name)
        last_name = self.string_cleaner.to_lower_and_trim(last_name)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert_contact(), (first_name, last_name))
            contact_id = c.lastrowid
            if contact_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_contact_id(), (first_name, last_name))
                contact_id = c.fetchone()[0]
            return contact_id

    def insert_alias(self, alias, return_existing_id=False):
        alias = self.string_cleaner.to_lower_and_trim(alias)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert_alias(), (alias,))
            alias_id = c.lastrowid
            if alias_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_alias_id(), (alias,))
                alias_id = c.fetchone()[0]
            return alias_id

    def link_contact_id_to_alias_id(self, contact_id, alias_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_contact_id_to_alias_id(), (contact_id, alias_id))
            conn.commit()

    def insert_email_address(self, email_address, return_existing_id=False):
        email_address = self.string_cleaner.to_lower_and_trim(email_address)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert_email_address(), (email_address,))
            address_id = c.lastrowid
            if address_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_email_address_id(), (email_address,))
                address_id = c.fetchone()[0]
            return address_id

    def link_contact_id_to_email_address_id(self, contact_id, address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_contact_id_to_email_address_id(), (contact_id, address_id))
            conn.commit()

    #--------------------------

    def insert_email(self, id, filepath, filename, subject, body, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert_email(), (id, filepath, filename, subject, body))
            email_id = c.lastrowid
            if email_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_email_id(), (email_id,))
                email_id = c.fetchone()[0]
            return email_id

    # --------------------------
    def insert_date(self, date, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert_date(), (date,))
            date_id = c.lastrowid
            if date_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_date_id(), (date,))
                date_id = c.fetchone()[0]
            return date_id

    def link_date_id_to_email_id(self, email_id, date_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_date_id_to_email_id(), (email_id, date_id))
            conn.commit()

    # --------------------------
    def insert_timestamp(self, timestamp, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert_timestamp(), (timestamp,))
            timestamp_id = c.lastrowid
            if timestamp_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_timestamp_id(), (timestamp,))
                timestamp_id = c.fetchone()[0]
            return timestamp_id

    def link_timestamp_id_to_email_id(self, email_id, timestamp_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_timestamp_id_to_email_id(), (email_id, timestamp_id))
            conn.commit()

    def link_from_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_from_email_address_id_to_email_id(), (email_id, email_address_id))
            conn.commit()

    def link_to_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_to_email_address_id_to_email_id(), (email_id, email_address_id))
            conn.commit()

    def link_cc_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_cc_email_address_id_to_email_id(), (email_id, email_address_id))
            conn.commit()

    def link_bcc_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_bcc_email_address_id_to_email_id(), (email_id, email_address_id))
            conn.commit()

    def insert_attachment(self, id, filename, content, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert_attachment(), (id, filename, content))
            attachment_id = c.lastrowid
            if attachment_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_attachment_id(), (attachment_id,))
                attachment_id = c.fetchone()[0]
            return attachment_id

    def link_attachment_id_to_email_id(self, email_id, attachment_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link_attachment_id_to_email_id(), (email_id, attachment_id))
            conn.commit()


