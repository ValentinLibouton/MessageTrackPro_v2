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

    def link_contact_id_to_alias_id(self, contact_id, alias_ids):
        request = self.sql_requests.link(table='Contacts_Alias',
                                         col_name_1='contact_id',
                                         col_name_2='alias_id')

        if isinstance(alias_ids, (list, tuple, set)):
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.executemany(request, [(contact_id, alias_id) for alias_id in alias_ids])
                conn.commit()
        else:
            alias_id = alias_ids
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute(request, (contact_id, alias_ids))
                conn.commit()

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

    def link_contact_id_to_email_address_id(self, contact_id, address_id):
        request = self.sql_requests.link(table='Contacts_EmailAddresses',
                                         col_name_1='contact_id',
                                         col_name_2='address_id')
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(request, (contact_id, address_id))
            conn.commit()

    #--------------------------

    def insert_email(self, id, filepath, filename, subject, body, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Emails',
                                               columns=['id', 'filepath', 'filename', 'subject', 'body'])
                      , (id, filepath, filename, subject, body))
            conn.commit()
            return id

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

    def insert_attachment(self, id, filename, content, return_existing_id=False):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(self.sql_requests.insert(table='Attachments',
                                               columns=['id', 'filename', 'content'])
                      , (id, filename, content))
            conn.commit()
            return id

    def link_attachment_id_to_email_id(self, email_id, attachment_ids):
        request = self.sql_requests.link(table='Email_Attachments',
                                         col_name_1='email_id',
                                         col_name_2='attachment_id')
        if isinstance(attachment_ids, (list, tuple, set)):
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.executemany(request, [(email_id, addr_id) for addr_id in attachment_ids])
                conn.commit()
        else:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute(request, (email_id, attachment_ids))
                conn.commit()



    # Todo: Je dois vérifier progressivement si la méthode ci-dessous peut remplacer les autres méthodes LINK ci-dessus

    def link(self, table, col_name_1, col_name_2, value_1, value_2, return_existing_id=False):
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


    # Todo: Je dois vérifier progressivement si la méthode ci-dessous peut remplacer les autres méthodes d'insert ci-dessus
    def insert(self, table, col_names, values, return_existing_id=False):
        if isinstance(col_names, str):
            col_names = [col_names]
        request = self.sql_requests.insert(table=table, columns=col_names)
        select = self.sql_requests.select_primary_key_from(table=table, columns=col_names)
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            if isinstance(values, (str, int, float, bool)): # simple insertion
                c.execute(request, (values,))
                if return_existing_id:
                    c.execute(select, (values,))
                    id = c.fetchone()
                    return id[0] if id else None
                return c.lastrowid

            if isinstance(values, set):
                values = tuple(values)

            if isinstance(values, (tuple, list)):
                if isinstance(values[0], (str, int, float, bool)) and len(col_names) > 1: # simple (first_name, last_name) = ('valentin', 'libouton)
                    c.execute((request, values))
                    if return_existing_id:
                        c.execute(select, values)
                        id = c.fetchone()
                        return id[0] if id else None
                    return c.lastrowid

                elif isinstance(values[0], (set, list, tuple)) and len(col_names) == 1: # Many (email_address) = ('abc@abc.be', def@def.com)
                    c.executemany(request, [(v,) for v in values])
                    ids = []
                    if return_existing_id:
                        for v in values:
                            c.execute(select, (v,))
                            fetched_id = c.fetchone()
                            if fetched_id:
                                ids.append(fetched_id[0])
                            else:
                                ids.append(None)
                    else:
                        ids = [None] * len(values)
                    return ids if len(ids) > 1 else ids[0]

            raise ValueError("Invalid data structure for 'values'")





