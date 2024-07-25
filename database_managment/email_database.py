import sqlite3
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import time
from datetime import timedelta

class EmailDatabase:
    def __init__(self, db_name='database.db'):
        self._db_name = db_name
        self._create_tables()
        self.unique_values = {
            'contacts': set(),
            'aliases': set(),
            'email_addresses': set(),
            'email_ids': set(),
            'attachments_ids': set()
        }

    def _create_tables(self):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Contacts (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT)'''

        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Alias (
            id INTEGER PRIMARY KEY,
            alias TEXT)'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Contacts_Alias(
            contact_id INTEGER,
            alias_id INTEGER,
            FOREIGN KEY(contact_id) REFERENCES Contacts(id),
            FOREIGN KEY(alias_id) REFERENCES Alias(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS EmailAddresses(
            id INTEGER PRIMARY KEY,
            email_address TEXT UNIQUE)'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Contacts_EmailAddresses(
            contact_id INTEGER,
            email_address_id INTEGER,
            FOREIGN KEY(contact_id) REFERENCES Contacts(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Emails (
            id TEXT PRIMARY KEY,
            filepath TEXT,
            filename TEXT,
            from_id INTEGER,
            subject TEXT,
            date TEXT,
            date_iso8601 TEXT,
            body TEXT,
            FOREIGN KEY(from_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_To(
            email_id TEXT,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_Cc(
            email_id TEXT,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_Bcc(
            email_id TEXT,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Attachments(
            id TEXT PRIMARY KEY,
            filename TEXT,
            content BLOB)'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_Attachments(
            email_id TEXT,
            attachment_id TEXT,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(attachment_id) REFERENCES Attachments(id))'''
        )

        conn.commit()
        conn.close()

    def _execute_query(self, query, params):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        c.execute(query, params)
        last_id = c.lastrowid
        conn.commit()
        conn.close()
        return last_id

    def _execute_many(self, query, params, ids=None):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        if ids is not None:
            params_with_ids = [(ids[i],) + param for i, param in enumerate(params)]
            c.executemany(query, params_with_ids)
        else:
            c.executemany(query, params)
        last_ids = [c.lastrowid for _ in params]
        conn.commit()
        conn.close()
        return last_ids

    def _value_exist_in_db(self, table, columns, values):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        conditions = ' AND '.join(f"{column} = ?" for column in columns)
        query = f'''SELECT id FROM {table} WHERE {conditions}'''
        c.execute(query, values)
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def _values_exist_in_db(self, table, columns, values_list):
        if not values_list:
            return {}
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        placeholders = ', '.join('?' for _ in columns)
        #query = f"SELECT id, {', '.join(columns)} FROM {table} WHERE ({', '.join(columns)}) IN ({placeholders})"
        query = f"SELECT id, {', '.join(columns)} FROM {table} WHERE ({', '.join(columns)}) IN ({', '.join(['(' + placeholders + ')' for _ in values_list])})"
        c.execute(query, [item for sublist in values_list for item in sublist])
        rows = c.fetchall()
        conn.close()
        return {tuple(row[1:]): row[0] for row in rows}

    def _value_exist(self, data_name: str, values: tuple, table: str, columns: tuple):
        if values not in self.unique_values[data_name]:
            id = self._value_exist_in_db(table=table, columns=columns, values=values)
            if id is None:
                columns_str = ', '.join(columns)
                placeholders = ', '.join('?' for _ in values)
                query = f'''INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})'''
                id = self._execute_query(query=query, params=values)
            self.unique_values[data_name].add(values)
            return id
        else:
            return self._value_exist_in_db(table=table, columns=columns, values=values)

    def _values_exist(self, data_name: str, values_list: list, table: str, columns: tuple):
        value_set = set(values_list)
        unique_values_set = self.unique_values[data_name]
        values_not_in_unique = value_set - unique_values_set
        if values_not_in_unique:
            existing_values = self._values_exist_in_db(table=table, columns=columns, values_list=list(values_not_in_unique))
            existing_values_set = set(existing_values.keys())
            new_values = values_not_in_unique - existing_values_set
            if new_values:
                columns_str = ', '.join(columns)
                placeholders = ', '.join('?' for _ in columns)
                query = f'''INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})'''
                self._execute_many(query, list(new_values))
                new_existing_values = self._values_exist_in_db(table=table, columns=columns, values_list=list(new_values))
                existing_values.update(new_existing_values)
                unique_values_set.update(new_existing_values.keys())
            return existing_values
        else:
            return {}

    def _id_exist_in_db(self, table, id):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        query = f"SELECT 1 FROM {table} WHERE id = ?"
        c.execute(query, (id,))
        result = c.fetchone()
        conn.close()
        return result is not None

    def _ids_exist_in_db(self, table, ids):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        placeholders = ', '.join('?' for _ in ids)
        query = f"SELECT id FROM {table} WHERE id IN ({placeholders})"
        c.execute(query, ids)
        result = c.fetchall()
        conn.close()
        return {row[0] for row in result}

    def _remove_duplicates(self, dict_list):
        """Remove dictionaries with duplicate 'id' keys from a list of dictionaries."""
        seen_ids = set()
        unique_dicts = []
        for d in dict_list:
            if d['id'] not in seen_ids:
                unique_dicts.append(d)
                seen_ids.add(d['id'])
        return unique_dicts

    def insert_contact(self, first_name, last_name):
        args = {
            'data_name': 'contacts',
            'values': (first_name, last_name),
            'table': 'Contacts',
            'columns': ('first_name', 'last_name')
        }
        return self._value_exist(**args)

    def insert_contacts(self, contacts:list):
        """
        Insert multiples contacts into database
        :param contacts: list(tuple(first_name, last_name))
        :return: list of ids
        """
        args = {
            'data_name': 'contacts',
            'values_list': contacts,
            'table': 'Contacts',
            'columns': ('first_name', 'last_name')
        }
        return self._values_exist(**args)

    def insert_alias(self, alias):
        args = {
            'data_name': 'aliases',
            'values': (alias,),
            'table': 'Alias',
            'columns': ('alias',)
        }
        return self._value_exist(**args)

    def insert_aliases(self, aliases):
        list_of_tuples = [(alias,) for alias in aliases]
        args = {
            'data_name': 'aliases',
            'values_list': list_of_tuples,
            'table': 'Alias',
            'columns': ('alias',)
        }
        return self._values_exist(**args)

    def link_alias_to_contact(self, contact_id, alias_id):
        query = '''INSERT OR IGNORE INTO Contacts_Alias(contact_id, alias_id) VALUES (?, ?)'''
        return self._execute_query(query, (contact_id, alias_id))

    def link_aliases_to_contacts(self, list_of_tuples):
        """
        Link multiples aliases to multiples contacts
        :param list_of_tuples: list(tuples(contact_id, alias_id))
        :returns: list of ids
        """
        query = '''INSERT OR IGNORE INTO Contacts_Alias(contact_id, alias_id) VALUES (?, ?)'''
        return self._execute_many(query, list_of_tuples)

    def insert_email_address(self, email_addr):
        args = {
            'data_name': 'email_addresses',
            'values': (email_addr,),
            'table': 'EmailAddresses',
            'columns': ('email_address',)
        }
        return self._value_exist(**args)

    def insert_email_addresses(self, emails_addr):
        list_of_tuples = [(email_addr,) for email_addr in emails_addr]
        args = {
            'data_name': 'email_addresses',
            'values_list': list_of_tuples,
            'table': 'EmailAddresses',
            'columns': ('email_address',)
        }
        return self._values_exist(**args)

    def link_email_address_to_contact(self, contact_id, email_address_id):
        query = '''INSERT OR IGNORE INTO Contact_EmailAddresses(contact_id, email_address_id) VALUES (?, ?)'''
        return self._execute_query(query, (contact_id, email_address_id))

    def link_email_addresses_to_contacts(self, list_of_tuples):
        query = '''INSERT OR IGNORE INTO Contact_EmailAddresses(contact_id, email_address_id) VALUES (?, ?)'''
        return self._execute_many(query, list_of_tuples)

    def insert_email(self, email):
        """
        :param email: tuple(id, filepath, filename, from_id, subject, date, date_iso8601, body)
        """
        id = email[0]
        if id not in self.unique_values['email_ids']:
            if self._id_exist_in_db('Emails', id):
                self.unique_values['email_ids']
            else:
                query = '''INSERT INTO Emails (id, filepath, filename, from_id, subject, date, date_iso8601, body) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                params = email
                self._execute_query(query, params)
                self.unique_values['email_ids'].add(id)
        return id


    def insert_emails(self, emails):
        # ToDo faire différemment ici pour tester uniquement la présence de l'id
        email_ids = [email[0] for email in emails]
        existing_ids = self.unique_values['email_ids'] | self._ids_exist_in_db('Emails', email_ids)

        new_emails = [email for email in emails if email[0] not in existing_ids]

        if new_emails:
            query = '''INSERT INTO Emails (id, filepath, filename, from_id, subject, date, date_iso8601, body) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            self._execute_many(query, new_emails)
            self.unique_values['email_ids'].update(email[0] for email in emails)

        return [email[0] for email in emails]

    def link_recipient(self, email_id, email_address_id):
        query = '''INSERT OR IGNORE INTO Email_To (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_query(query, (email_id, email_address_id))

    def link_recipients(self, recipients):
        query = '''INSERT OR IGNORE INTO Email_To (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_many(query, recipients)

    def link_cc(self, email_id, email_address_id):
        query = '''INSERT OR IGNORE INTO Email_Cc (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_query(query, (email_id, email_address_id))

    def link_ccs(self, ccs):
        query = '''INSERT OR IGNORE INTO Email_Cc (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_many(query, ccs)

    def link_bcc(self, email_id, email_address_id):
        query = '''INSERT OR IGNORE INTO Email_Bcc (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_query(query, (email_id, email_address_id))

    def link_bccs(self, bccs):
        query = '''INSERT OR IGNORE INTO Email_Bcc (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_many(query, bccs)

    def insert_attachment(self, id, email_id, filename, content):
        # ToDo faire différemment ici pour tester uniquement la présence de l'id
        query = '''INSERT INTO Attachments (id, filename, content) VALUES (?, ?, ?)'''
        return self._execute_query(query, (email_id, filename, content))

    def insert_attachments(self, attachments):
        unique_attachments = self._remove_duplicates(attachments)
        attachment_ids = [att['id'] for att in unique_attachments]
        existing_ids = self.unique_values['attachments_ids'] | set(self._ids_exist_in_db('Attachments', attachment_ids))

        new_attachments = [attachment for attachment in unique_attachments if attachment['id'] not in existing_ids]
        if new_attachments:
            query = '''INSERT INTO Attachments (id, filename, content) VALUES (?, ?, ?)'''
            self._execute_many(query, [(att['id'], att['filename'], att['content']) for att in new_attachments])
            self.unique_values['attachments_ids'].update(att['id'] for att in new_attachments)

        return attachment_ids

    def link_attachments_to_email(self, email_id, attachment_ids):
        query = '''INSERT INTO Email_Attachments (email_id, attachment_id) VALUES (?, ?)'''
        params = [(email_id, attachment_id) for attachment_id in attachment_ids]
        self._execute_many(query, params)


    def get_email_address_id(self, email):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        c.execute('''SELECT id FROM EmailAddresses WHERE email_address = ?''', (email,))
        email_address_id = c.fetchone()
        conn.close()
        return email_address_id[0] if email_address_id else None

class EmailLoader:
    def __init__(self, emails: list, db_name='database.db'):
        self.db = EmailDatabase(db_name)
        self._time_dict = {}
        self._emails = emails
        self._load_emails_into_db(emails=self._emails)

    def _load_email_into_db(self, email):
        from_email = email['from_email']
        from_name = email['from_name']
        from_email_id = self.db.insert_email_address(email_addr=from_email)
        contact_alias_id = self.db.insert_alias(alias=from_name)

        email_data = (email['id'], email['filepath'], email['filename'], from_email_id, email['subject'], str(email['date_obj']),
                      str(email['date_iso8601']), email['body'])
        email_id = self.db.insert_email(email_data)

        if email['to_emails']:
            email_address_ids = list(self.db.insert_email_addresses(email['to_emails']).values())
            self.db.link_recipients([(email_id, email_address_id) for email_address_id in email_address_ids])

        if email['cc_emails']:
            email_address_ids = list(self.db.insert_email_addresses(email['cc_emails']).values())
            self.db.link_ccs([(email_id, email_address_id) for email_address_id in email_address_ids])

        if email['bcc_emails']:
            email_address_ids = list(self.db.insert_email_addresses(email['bcc_emails']).values())
            self.db.link_bccs([(email_id, email_address_id) for email_address_id in email_address_ids])

        if email['attachments']:
            #attachments = [(att['id'], att['filename'], att['content']) for att in email['attachments']]
            attachment_ids = self.db.insert_attachments(email['attachments'])
            self.db.link_attachments_to_email(email_id, attachment_ids)

    def _load_emails_into_db(self, emails, multi_processing=False):
        start_time = time.time()
        # ToDo: Multiprocessing does not save db insertion time!
        if multi_processing:
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self._load_email_into_db, email) for email in emails]
                for future in tqdm(as_completed(futures), total=len(futures), desc="Load emails into db"):
                    future.result()
        else:
            for email in tqdm(emails, desc="Load emails into db"):
                self._load_email_into_db(email)
        end_time = time.time()
        self._time_dict['Load emails into db'] = end_time - start_time

    @property
    def log_execution_time(self):
        if self._time_dict:
            for text, seconds in self._time_dict.items():
                elapsed_time = timedelta(seconds=seconds)
                hours, remainder = divmod(elapsed_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                if elapsed_time.days > 0:
                    print(
                        f"{text}: {elapsed_time.days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
                elif hours > 0:
                    print(f"{text}: {hours} hours, {minutes} minutes, {seconds} seconds")
                elif minutes > 0:
                    print(f"{text}: {minutes} minutes, {seconds} seconds")
                else:
                    print(f"{text}: {seconds} seconds")

