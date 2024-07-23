import sqlite3
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import time

class EmailDatabase:
    def __init__(self, db_name='database.db'):
        self._db_name = db_name
        self._create_tables()

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
            email_id INTEGER,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_Cc(
            email_id INTEGER,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Email_Bcc(
            email_id INTEGER,
            email_address_id INTEGER,
            FOREIGN KEY(email_id) REFERENCES Emails(id),
            FOREIGN KEY(email_address_id) REFERENCES EmailAddresses(id))'''
        )

        c.execute(
            '''CREATE TABLE IF NOT EXISTS Attachments(
            id INTEGER PRIMARY KEY,
            email_id INTEGER,
            filename TEXT,
            content BLOB,
            FOREIGN KEY(email_id) REFERENCES Emails(id))'''
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
        query = '''INSERT OR IGNORE INTO Alias(alias) VALUES (?)'''
        return self._execute_query(query, (alias,))

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
        query = '''INSERT INTO Emails (id, filepath, filename, from_id, subject, date, date_iso8601, body)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        return self._execute_query(query, email)

    def insert_emails(self, emails):
        query = '''INSERT INTO Emails (id, filepath, filename, from_id, subject, date, date_iso8601, body)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        return self._execute_many(query, emails)

    def link_recipient(self, email_id, email_address_id):
        query = '''INSERT INTO Email_To (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_query(query, (email_id, email_address_id))

    def link_recipients(self, recipients):
        query = '''INSERT INTO Email_To (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_many(query, recipients)

    def link_cc(self, email_id, email_address_id):
        query = '''INSERT INTO Email_Cc (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_query(query, (email_id, email_address_id))

    def link_ccs(self, ccs):
        query = '''INSERT INTO Email_Cc (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_many(query, ccs)

    def link_bcc(self, email_id, email_address_id):
        query = '''INSERT INTO Email_Bcc (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_query(query, (email_id, email_address_id))

    def link_bccs(self, bccs):
        query = '''INSERT INTO Email_Bcc (email_id, email_address_id) VALUES (?, ?)'''
        self._execute_many(query, bccs)

    def get_email_address_id(self, email):
        conn = sqlite3.connect(self._db_name)
        c = conn.cursor()
        c.execute('''SELECT id FROM EmailAddresses WHERE email_address = ?''', (email,))
        email_address_id = c.fetchone()
        conn.close()
        return email_address_id[0] if email_address_id else None


def process_email(email, db):
    from_email = email['from_email']
    from_name = email['from_name']
    from_email_id = db.insert_email_address(email=from_email)
    contact_alias_id = db.insert_contact_alias(alias=from_name)


    email_data = (email['id'], email['filepath'], email['filename'], from_email_id, email['subject'], str(email['date_obj']),
                  str(email['date_iso8601']), email['body'])
    email_id = db.insert_email(email_data)

    if email['to_emails']:
        recipients = [(email_id, db.get_email_address_id(recipient)) for recipient in email['to_emails']]
        db.link_recipients(recipients)

    if email['cc_emails']:
        ccs = [(email_id, db.get_email_address_id(cc)) for cc in email['cc_emails']]
        db.link_ccs(ccs)

    if email['bcc_emails']:
        bccs = [(email_id, db.get_email_address_id(bcc)) for bcc in email['bcc_emails']]
        db.link_bccs(bccs)

    # ToDo: insertion of attachments below


def process_emails(emails):
    start_time = time.time()
    db = EmailDatabase()
    # ToDo: Multiprocessing does not save db insertion time!
    #with ProcessPoolExecutor() as executor:
    #    futures = [executor.submit(process_email, email, db) for email in emails]
    #    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing emails"):
    #        future.result()
    for email in tqdm(emails, desc="Processing emails"):
        process_email(email, db)
    end_time = time.time()
    print(f"Processed {len(emails)} emails in {end_time - start_time} seconds")