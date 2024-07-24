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
            'aliases': set(),
            'email_addresses': set(),
            'attachments_id': set()
        }

    def _create_tables(self):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Contact (
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
            '''CREATE TABLE IF NOT EXISTS Contact_Alias(
            contact_id INTEGER,
            alias_id INTEGER,
            FOREIGN KEY(contact_id) REFERENCES Contact(id),
            FOREIGN KEY(alias_id) REFERENCES Alias(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS EmailAddresses(
            id INTEGER PRIMARY KEY,
            email_address TEXT UNIQUE)'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Contact_EmailAddresses(
            contact_id INTEGER,
            email_address_id INTEGER,
            FOREIGN KEY(contact_id) REFERENCES Contact(id),
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
            '''CREATE TABLE IF NOT EXISTS EmailAttachments(
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

    def _value_exists(self, table, column, value):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        query = f'''SELECT id FROM {table} WHERE {column} = ?'''
        c.execute(query, (value,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def insert_contact(self, first_name, last_name):
        query = '''INSERT OR IGNORE INTO Contacts(first_name, last_name) VALUES (?,?)'''
        return self._execute_query(query, (first_name, last_name))

    def insert_contacts(self, contacts):
        """
        Insert multiples contacts into database
        :param contacts: list(tuple(first_name, last_name))
        :return: list of ids
        """
        query = '''INSERT OR IGNORE INTO Contacts(first_name, last_name) VALUES (?,?)'''
        return self._execute_many(query, contacts)

    def insert_contact_alias(self, alias):
        if alias not in self.unique_values['aliases']:
            id = self._value_exists(table='Alias', column='alias', value=alias)
            if id is not None:
                self.unique_values['aliases'].add(alias)
                return id
            else:
                query = '''INSERT OR IGNORE INTO Alias(alias) VALUES (?)'''
                alias_id = self._execute_query(query, (alias,))
                self.unique_values['aliases'].add(alias_id)
                return alias_id

    def insert_contact_aliases(self, aliases):
        query = '''INSERT OR IGNORE INTO Alias(alias) VALUES (?)'''
        return self._execute_many(query, [(alias,) for alias in aliases])

    def link_alias_to_contact(self, contact_id, alias_id):
        query = '''INSERT OR IGNORE INTO ContactAlias(contact_id, alias_id) VALUES (?, ?)'''
        return self._execute_query(query, (contact_id, alias_id))

    def link_aliases_to_contacts(self, list_of_tuples):
        """
        Link multiples aliases to multiples contacts
        :param list_of_tuples: list(tuples(contact_id, alias_id))
        :returns: list of ids
        """
        query = '''INSERT OR IGNORE INTO ContactAlias(contact_id, alias_id) VALUES (?, ?)'''
        return self._execute_many(query, list_of_tuples)

    def insert_email_address(self, email):
        query = '''INSERT OR IGNORE INTO EmailAddresses (email_address) VALUES (?)'''
        return self._execute_query(query, (email,))

    def insert_email_addresses(self, emails):
        query = '''INSERT OR IGNORE INTO EmailAddresses (email_address) VALUES (?)'''
        return self._execute_many(query, [(email,) for email in emails])

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
        query = '''INSERT OR IGNORE INTO Emails (id, filepath, filename, from_id, subject, date, date_iso8601, body)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        return self._execute_query(query, email)

    def insert_emails(self, emails):
        query = '''INSERT OR IGNORE INTO Emails (id, filepath, filename, from_id, subject, date, date_iso8601, body)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        return self._execute_many(query, emails)

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
        query = '''INSERT INTO Attachments (id, filename, content) VALUES (?, ?, ?)'''
        return self._execute_query(query, (email_id, filename, content))

    def insert_attachments(self, attachments):
        query = '''INSERT INTO Attachments (id, filename, content) VALUES (?, ?, ?)'''
        new_attachments = []
        for attachment in attachments:
            attachment_id = attachment[0]
            if attachment_id not in self.unique_values['attachments_id']:
                id = self._value_exists(table='Attachments', column='id', value=attachment_id)
                if id is not None:
                    self.unique_values['attachments_id'].add(attachment_id)
                else:
                    new_attachments.append(attachment)
                    self.unique_values['attachments_id'].add(attachment_id)
        if new_attachments:
            return self._execute_many(query, new_attachments)
        return [attachment[0] for attachment in attachments]

    def link_attachments_to_email(self, email_id, attachment_ids):
        query = '''INSERT INTO EmailAttachments (email_id, attachment_id) VALUES (?, ?)'''
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
        from_email_id = self.db.insert_email_address(email=from_email)
        contact_alias_id = self.db.insert_contact_alias(alias=from_name)

        email_data = (email['id'], email['filepath'], email['filename'], from_email_id, email['subject'], str(email['date_obj']),
                      str(email['date_iso8601']), email['body'])
        email_id = self.db.insert_email(email_data)

        if email['to_emails']:
            recipients = [(email_id, self.db.get_email_address_id(recipient)) for recipient in email['to_emails']]
            self.db.link_recipients(recipients)

        if email['cc_emails']:
            ccs = [(email_id, self.db.get_email_address_id(cc)) for cc in email['cc_emails']]
            self.db.link_ccs(ccs)

        if email['bcc_emails']:
            bccs = [(email_id, self.db.get_email_address_id(bcc)) for bcc in email['bcc_emails']]
            self.db.link_bccs(bccs)

        if email['attachments']:
            attachments = [(att['id'], att['filename'], att['content']) for att in email['attachments']]
            attachment_ids = self.db.insert_attachments(attachments)
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

