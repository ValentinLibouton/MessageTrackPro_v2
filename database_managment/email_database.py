import sqlite3
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import time
from datetime import timedelta


class EmailDatabase:
    def __init__(self, db_name='database.db'):
        self._db_name = db_name
        self._create_tables()

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


    def process_simple_insertion(self, datas, table, columns):
        """Pour les tables:
            - Contacts
            - Alias
            - EmailAddress

        """
    def process_link_insertion(self, ids, table, columns):
        """Pour les tables:
            - Contacts_Alias
            - Contacts_EmailAddresses
            - Email_To
            - Email_Cc
            - Email_Bcc
            - Email_Attachments
            """
    def process_email_insertion(self):
        pass

    def process_attachments_insertion(self):
        pass


class EmailLoader:
    def __init__(self, datas:dict, db_name='database.db'):
        self.db = EmailDatabase(db_name)
        self._time_dict = {}
        self.datas = datas
        self._load_datas_into_db(emails=self._emails)


    def _load_datas_into_db(self):
        self.db.
        self.datas['all_email_addresses']

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
