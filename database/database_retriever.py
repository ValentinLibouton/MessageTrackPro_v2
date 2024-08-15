import sqlite3
from database.sql_request import SQLRequest
class DatabaseRetriever:
    def __init__(self, db_name='../database.db',
                 contact: list = None,
                 aliases: list = None,
                 addresses: list = None,
                 start_date: str = None,
                 end_date: str = None,

                 words_everywhere: list = None,
                 words_in_contact: list = None,
                 words_in_address: list = None,
                 words_in_subject: list = None,
                 words_in_body: list = None,
                 words_in_attachment_names: list = None,
                 words_in_attachment: list = None,
                 # Todo ...

                 attachment_types: list = None,
                 include_attachments: bool = True):

        #self.sql_requests = SQLRequest()

        self.db_name = db_name
        self.contacts = contact  # [(first_name_1, last_name_1), (first_name_2, last_name_2)]
        self.addresses = addresses
        self.words_in_address = words_in_address
        self.start_date = str(start_date) if start_date is not None else ""
        self.end_date = str(end_date) if end_date is not None else ""
        self.words_everywhere = words_everywhere
        self.request = ""

    def execute(self, request, params):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(request, params)
            results = c.fetchall()
        return results

    def select_email_id(self):
        self.request = f"""SELECT e.id FROM Emails e"""
        return self

    def join(self):
        #if self.words_everywhere is not None: #or self.addresses is not None or self.words_in_address is not None or self.first_name is not None or self.last_name is not None:
        # Todo: je dois filtrer les JOIN pour retirer ceux qui ne sont pas nécessaires en fonction de la requete utilisateur

        # Joindre les tables des emails
        self.request += f""" JOIN Email_From ef ON e.id = ef.email_id"""
        self.request += f""" JOIN Email_To et ON e.id = et.email_id"""
        self.request += f""" JOIN Email_Cc ec ON e.id = ec.email_id"""
        self.request += f""" JOIN Email_Bcc eb ON e.id = eb.email_id"""

        # Joindre les adresses email
        self.request += f""" JOIN EmailAddresses ea1 ON ea1.id = ef.email_address_id"""
        self.request += f""" JOIN EmailAddresses ea2 ON ea2.id = et.email_address_id"""
        self.request += f""" JOIN EmailAddresses ea3 ON ea3.id = ec.email_address_id"""
        self.request += f""" JOIN EmailAddresses ea4 ON ea4.id = eb.email_address_id"""

        # Joindre les contacts et alias
        self.request += f""" JOIN Contacts_EmailAddresses cea1 ON ea1.id = cea1.email_address_id"""
        self.request += f""" JOIN Contacts_EmailAddresses cea2 ON ea2.id = cea2.email_address_id"""
        self.request += f""" JOIN Contacts_EmailAddresses cea3 ON ea3.id = cea3.email_address_id"""
        self.request += f""" JOIN Contacts_EmailAddresses cea4 ON ea4.id = cea4.email_address_id"""

        self.request += f""" JOIN Contacts_Alias ca ON cea1.contact_id = ca.contact_id"""
        self.request += f""" JOIN Alias a ON ca.alias_id = a.id"""
        self.request += f""" JOIN Contacts c ON ca.contact_id = c.id"""

        # Joindre les dates
        self.request += f""" JOIN Email_Date ed ON e.id = ed.email_id"""
        self.request += f""" JOIN Date d ON ed.date_id = d.id"""

        # Joindre les pièces jointes
        self.request += f""" JOIN Email_Attachments ea ON e.id = ea.email_id"""
        self.request += f""" JOIN Attachments att ON ea.attachment_id = att.id"""






    def all_words_search(self, table, columns, words):
        request = f"""SELECT id FROM {table} WHERE """
        conditions = []

        for word in words:
            word_conditions = []
            for column in columns:
                word_conditions.append(f"LOWER({column}) LIKE '%' || LOWER(?) || '%'")
            conditions.append(f"({' OR '.join(word_conditions)})")

        request += " AND ".join(conditions)
        return self




    def _simple_word_search(self, table, columns, word):
        request = self.sql_requests.simple_word_search(table=table, columns=columns)
        parameters = tuple([word.lower()] * len(columns))
        # print(f"Request:\n{request}")
        # print(f"Parameters:\n{parameters}")

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            # print(c.fetchall())
            c.execute(request, parameters)
            results = c.fetchall()
        return results

    def _all_words_search(self, table, columns, words):
        request = self.sql_requests.all_words_search(table=table, columns=columns,words=words)
        parameters = tuple(word.lower() for word in words for _ in columns)
        # print(f"Request:\n{request}")
        # print(f"Parameters:\n{parameters}")

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(request, parameters)
            results = c.fetchall()
        return results

    def _any_words_search(self, table, columns, words, ids=None):
        request = self.sql_requests.any_word_search(table=table, columns=columns,words=words, ids=ids)
        if ids is not None:
            pass
        else:
            parameters = tuple(word.lower() for word in words for _ in columns)
        # print(f"Request:\n{request}")
        # print(f"Parameters:\n{parameters}")

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(request, parameters)
            results = c.fetchall()
        return results
