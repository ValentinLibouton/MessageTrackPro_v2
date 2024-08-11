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
        first_name = self.string_cleaner.to_lower_and_trim(first_name)
        last_name = self.string_cleaner.to_lower_and_trim(last_name)
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
        alias = self.string_cleaner.to_lower_and_trim(alias)
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

    def link_contact_id_to_alias_id(self, contact_id, alias_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Contacts_Alias',
                                             pk_1=contact_id,
                                             pk_2=alias_id), (contact_id, alias_id))
            conn.commit()

    def insert_email_address(self, email_address, return_existing_id=False):
        email_address = self.string_cleaner.to_lower_and_trim(email_address)
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

    def link_contact_id_to_email_address_id(self, contact_id, address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Contacts_EmailAddresses',
                                             pk_1=contact_id,
                                             pk_2=address_id), (contact_id, address_id))
            conn.commit()

    #--------------------------

    def insert_email(self, id, filepath, filename, subject, body, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Emails',
                                               columns=['id', 'filepath', 'filename', 'subject', 'body'])
                      , (id, filepath, filename, subject, body))
            email_id = c.lastrowid
            if email_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table='Emails',
                                                                    columns=['id']), (email_id,))
                email_id = c.fetchone()[0]
            return email_id

    # --------------------------
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

    def link_date_id_to_email_id(self, email_id, date_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_Date',
                                             pk_1=email_id,
                                             pk_2=date_id), (email_id, date_id))
            conn.commit()

    # --------------------------
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

    def link_timestamp_id_to_email_id(self, email_id, timestamp_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_Timestamp',
                                             pk_1=email_id,
                                             pk_2=timestamp_id), (email_id, timestamp_id))
            conn.commit()

    def link_from_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_From',
                                             pk_1=email_id,
                                             pk_2=email_address_id), (email_id, email_address_id))
            conn.commit()

    def link_to_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_To',
                                             pk_1=email_id,
                                             pk_2=email_address_id), (email_id, email_address_id))
            conn.commit()

    def link_cc_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_Cc',
                                             pk_1=email_id,
                                             pk_2=email_address_id), (email_id, email_address_id))
            conn.commit()

    def link_bcc_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_Bcc',
                                             pk_1=email_id,
                                             pk_2=email_address_id), (email_id, email_address_id))
            conn.commit()

    def insert_attachment(self, id, filename, content, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Attachments',
                                               columns=['id', 'filename', 'content'])
                      , (id, filename, content))
            attachment_id = c.lastrowid
            if attachment_id == 0 and return_existing_id:
                c.execute(self.sql_requests.select_primary_key_from(table='Attachments',
                                                                    columns=['id']), (attachment_id,))
                attachment_id = c.fetchone()[0]
            return attachment_id

    def link_attachment_id_to_email_id(self, email_id, attachment_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_Attachments',
                                             pk_1=email_id,
                                             pk_2=attachment_id), (email_id, attachment_id))
            conn.commit()


