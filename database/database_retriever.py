import sqlite3
from database.sql_request import SQLRequest
from utils.date_transformer import DateTransformer
class DatabaseRetriever:
    def __init__(self, db_name='../database.db', **kwargs):
        """
        : contacts: filtering on specific contacts
        : aliases: filtering on specific aliases
        : addresses: filtering on specific email addresses
        : start_date: filtering on start date
        : end_date: filtering on end date
        :words_localization: list of words localization ['everywhere', 'contact', 'alias', 'address',
                                'subject', 'body', 'attachment_name', 'attachment']
        :attachment_types: filtering on attachment types

        """
        #self.sql_requests = SQLRequest()

        self.db_name = db_name
        self.params = kwargs
        self.words_localization_control()
        self.convert_to_timestamp()

        self.join_clauses = set()
        self.where_clauses = set()
        self.order_by_clause = ""
        self.limit_clause = ""
        self.request = ""

    def words_localization_control(self):
        valid_localization = ['everywhere', 'contact', 'alias', 'address', 'subject', 'body', 'attachment_name', 'attachment']
        words_localization = self.params.get('words_localization', [])
        if 'everywhere' in words_localization:
            self.params['words_localization'] = ['everywhere']
        else:
            for localization in words_localization:
                if localization not in valid_localization[1:]: # everywhere already processed
                    raise ValueError(f"{localization} is not a valid words localization, valid values are: {valid_localization}")

    def date_to_timestamp(self):
        dt = DateTransformer()
        if self.params['start_date']:
            self.start_timestamp = dt.convert_to_timestamp(self.params['start_date'])
        else:
            self.start_timestamp = 0
        if self.params['end_date']:
            self.end_timestamp = dt.convert_to_timestamp(self.params['end_date'])
        else:
            self.end_timestamp = None

    def select(self):
        self.request = f"""SELECT e.id FROM Emails e"""
        return self

    def add_join(self, join_clause):
        if join_clause not in self.join_clauses:
            self.request += f" {join_clause}"
            self.join_clauses.add(join_clause)

    def add_where(self, condition):
        self.where_clauses.add(condition)
        return self

    def add_order_by(self, columns, ascending=True):
        order = "ASC" if ascending else "DESC"
        self.order_by_clause += f"ORDER BY {', '.join(columns)} {order}"

    def add_limit(self, limit):
        self.limit_clause = f"LIMIT {limit}"
        return self

    def build_query(self):
        query = self.select()
        if self.join_clauses:
            query += " " + " ".join(self.join_clauses)
        if self.where_clauses:
            query += " WHERE " + " AND ".join(self.where_clauses)
        if self.order_by_clause:
            query += " " + self.order_by_clause
        if self.limit_clause:
            query += " " + self.limit_clause
        return query

    def join(self):
        if 'everywhere' in self.params.get('words_localization', []):
            self.add_join("JOIN Email_From ef ON e.id = ef.email_id")
            self.add_join("JOIN Email_To ef ON e.id = et.email_id")
            self.add_join("JOIN Email_Cc ec ON e.id = ec.email_id")
            self.add_join("JOIN Email_Bcc eb ON e.id = eb.email_id")

            self.add_join("JOIN EmailAddresses ea1 ON ea1.id = ef.email_address_id")
            self.add_join("JOIN EmailAddresses ea2 ON ea2.id = et.email_address_id")
            self.add_join("JOIN EmailAddresses ea3 ON ea3.id = ec.email_address_id")
            self.add_join("JOIN EmailAddresses ea4 ON ea4.id = eb.email_address_id")

            self.add_join("JOIN Contacts_EmailAddresses cea1 ON ea1.id = cea1.email_address_id")
            self.add_join("JOIN Contacts_EmailAddresses cea2 ON ea2.id = cea2.email_address_id")
            self.add_join("JOIN Contacts_EmailAddresses cea3 ON ea3.id = cea3.email_address_id")
            self.add_join("JOIN Contacts_EmailAddresses cea4 ON ea4.id = cea4.email_address_id")

            self.add_join("JOIN Contacts_Alias ca1 ON cea1.contact_id = ca1.contact_id")
            self.add_join("JOIN Contacts_Alias ca2 ON cea2.contact_id = ca2.contact_id")
            self.add_join("JOIN Contacts_Alias ca3 ON cea3.contact_id = ca3.contact_id")
            self.add_join("JOIN Contacts_Alias ca4 ON cea4.contact_id = ca4.contact_id")

            self.add_join("JOIN Alias a1 ON ca1.alias_id = a1.id")
            self.add_join("JOIN Alias a2 ON ca2.alias_id = a2.id")
            self.add_join("JOIN Alias a3 ON ca3.alias_id = a3.id")
            self.add_join("JOIN Alias a4 ON ca4.alias_id = a4.id")

            self.add_join("JOIN Contacts c1 ON ca1.contact_id = c1.id")
            self.add_join("JOIN Contacts c2 ON ca2.contact_id = c2.id")
            self.add_join("JOIN Contacts c3 ON ca3.contact_id = c3.id")
            self.add_join("JOIN Contacts c4 ON ca4.contact_id = c4.id")


            self.add_join("JOIN Contacts c5 ON cea1.contact_id = c5.id")
            self.add_join("JOIN Contacts c6 ON cea2.contact_id = c6.id")
            self.add_join("JOIN Contacts c7 ON cea3.contact_id = c7.id")
            self.add_join("JOIN Contacts c8 ON cea4.contact_id = c8.id")

            #self.add_join("JOIN Email_Date ed ON e.id = ed.email_id")
            #self.add_join("JOIN Date d ON ed.date_id = d.id")
            self.add_join("JOIN Email_Timestamp eti ON e.id = eti.email_id")
            self.add_join("JOIN Timestamp ts ON eti.timestamp_id = ts.id")

            self.add_join("JOIN Email_Attachments ea ON e.id = ea.email_id")
            self.add_join("JOIN Attachments att ON ea.attachment_id = att.id")

        if self.params.get('contacts') or 'contact' in self.params.get('words_localization', []):
            self.add_join("JOIN Email_From ef ON e.id = ef.email_id")
            self.add_join("JOIN Email_To ef ON e.id = et.email_id")
            self.add_join("JOIN Email_Cc ec ON e.id = ec.email_id")
            self.add_join("JOIN Email_Bcc eb ON e.id = eb.email_id")

            self.add_join("JOIN EmailAddresses ea1 ON ea1.id = ef.email_address_id")
            self.add_join("JOIN EmailAddresses ea2 ON ea2.id = et.email_address_id")
            self.add_join("JOIN EmailAddresses ea3 ON ea3.id = ec.email_address_id")
            self.add_join("JOIN EmailAddresses ea4 ON ea4.id = eb.email_address_id")

            self.add_join("JOIN Contacts_EmailAddresses cea1 ON ea1.id = cea1.email_address_id")
            self.add_join("JOIN Contacts_EmailAddresses cea2 ON ea2.id = cea2.email_address_id")
            self.add_join("JOIN Contacts_EmailAddresses cea3 ON ea3.id = cea3.email_address_id")
            self.add_join("JOIN Contacts_EmailAddresses cea4 ON ea4.id = cea4.email_address_id")

            self.add_join("JOIN Contacts c5 ON cea1.contact_id = c5.id")
            self.add_join("JOIN Contacts c6 ON cea2.contact_id = c6.id")
            self.add_join("JOIN Contacts c7 ON cea3.contact_id = c7.id")
            self.add_join("JOIN Contacts c8 ON cea4.contact_id = c8.id")

            # Todo: j'ai modifié ci-dessus, je dois encore modifier ci-dessous
        if self.params.get('aliases') or 'alias' in self.params.get('words_localization', []):
            self.add_join("JOIN Email_From ef ON e.id = ef.email_id")
            self.add_join("JOIN EmailAddresses ea1 ON ea1.id = ef.email_address_id")
            self.add_join("JOIN Contacts_EmailAddresses cea1 ON ea1.id = cea1.email_address_id")
            self.add_join("JOIN Contacts_Alias ca ON cea1.contact_id = ca.contact_id")
            self.add_join("JOIN Alias a ON ca.alias_id = a.id")

        if self.params.get('addresses') or 'address' in self.params.get('words_localization', []):
            self.add_join("JOIN Email_From ef ON e.id = ef.email_id")
            self.add_join("JOIN EmailAddresses ea1 ON ea1.id = ef.email_address_id")
            self.add_join("JOIN Contacts_EmailAddresses cea1 ON ea1.id = cea1.email_address_id")

        if self.params.get('start_date') or self.params.get('end_date'):
            #self.add_join("JOIN Email_Date ed ON e.id = ed.email_id")
            #self.add_join("JOIN Date d ON ed.date_id = d.id")
            self.add_join("JOIN Email_Timestamp eti ON e.id = eti.email_id")
            self.add_join("JOIN Timestamp ts ON eti.timestamp_id = ts.id")

        if self.params.get('attachment_types') or 'attachment' in self.params.get('words_localization', []) or 'attachment_name' in self.params.get('words_localization', []):
            self.add_join("JOIN Email_Attachments ea ON e.id = ea.email_id")
            self.add_join("JOIN Attachments att ON ea.attachment_id = att.id")

        return self

    def where(self):
        if self.params.get('start_date') and self.params.get('end_date'):
            self.add_where(f"ts.timestamp BETWEEN '{self.start_timestamp}' AND '{self.end_timestamp}'")
        elif self.params.get('start_date'):
            self.add_where(f"ts.timestamp >= '{self.start_timestamp}'")
        elif self.params.get('end_date'):
            self.add_where(f"ts.timestamp <= '{self.end_timestamp}'")

        if self.params.get('contacts'):
            contact_conditions = " OR ".join(
                [f"LOWER(c.first_name) = LOWER({first_name}) AND LOWER(c.last_name) = LOWER({last_name})"
                for first_name, last_name in self.params['contacts']])
            self.add_where(f"({contact_conditions})")

        if self.params.get('aliases'):
            alias_conditions = " OR ".join(
                [f"LOWER(a.alias) = LOWER('{alias}')" for alias in self.params['aliases']])
            self.add_where(f"({alias_conditions})")

        if self.params.get('addresses'):
            address_conditions = " OR ".join(
                [f"LOWER(ea1.address) = LOWER('{address}" for address in self.params['addresses']]
            )



        # ToDo: below....
        if 'contact' in self.params.get('words_localization', []):
            pass

    def execute(self, request, params):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(request, params)
            results = c.fetchall()
        return results






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
