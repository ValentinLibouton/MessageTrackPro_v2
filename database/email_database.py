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
                                             col_name_1=contact_id,
                                             col_name_2=alias_id), (contact_id, alias_id))
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
                                             col_name_1=contact_id,
                                             col_name_2=address_id), (contact_id, address_id))
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
                                             col_name_1=email_id,
                                             col_name_2=date_id), (email_id, date_id))
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
                                             col_name_1=email_id,
                                             col_name_2=timestamp_id), (email_id, timestamp_id))
            conn.commit()

    def link_from_email_address_id_to_email_id(self, email_id, email_address_ids):
        # Todo debugging here
        request = self.sql_requests.link(table='Email_From',
                                         col_name_1='email_id',
                                         col_name_2='email_address_id')
        print(f"Executing query: {request}")  # Debugging line
        print(f"With values: {email_id}, {email_address_ids}")
        if isinstance(email_address_ids, (list, tuple, set)):
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()

                #c.executemany(request, [(email_id, addr_id) for addr_id in email_address_ids])

                for addr_id in email_address_ids:
                    c.execute(f"INSERT OR IGNORE Email_From ('email_id', 'email_address_id') VALUES (?, ?)",
                              (str(email_id), addr_id))
                conn.commit()
        else:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute(request, (email_id, email_address_ids))
                conn.commit()

    def link_to_email_address_id_to_email_id(self, email_id, email_address_id):
        if isinstance(email_address_id, (list, tuple, set)):
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                request = self.sql_requests.link(table='Email_To',
                                                 col_name_1='email_id',
                                                 col_name_2='email_address_id')
                c.executemany(request, [(email_id, addr_id) for addr_id in email_address_id])
                conn.commit()
        else:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute(self.sql_requests.link(table='Email_To',
                                                 col_name_1=email_id,
                                                 col_name_2=email_address_id), (email_id, email_address_id[0]))
                conn.commit()

    def link_cc_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_Cc',
                                             col_name_1=email_id,
                                             col_name_2=email_address_id), (email_id, email_address_id))
            conn.commit()

    def link_bcc_email_address_id_to_email_id(self, email_id, email_address_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.link(table='Email_Bcc',
                                             col_name_1=email_id,
                                             col_name_2=email_address_id), (email_id, email_address_id))
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
                                             col_name_1=email_id,
                                             col_name_2=attachment_id), (email_id, attachment_id))
            conn.commit()


