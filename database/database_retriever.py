import sqlite3
from database.sql_request import SQLRequest
class DatabaseRetriever:
    def __init__(self, db_name='../database.db'):
        self.db_name = db_name
        self.sql_requests = SQLRequest()
        print(f"Connected to database: {self.db_name}")

    def simple_word_search(self, table, columns, word):
        request = self.sql_requests.simple_word_search(table=table, columns=columns)
        parameters = tuple([word.lower()] * len(columns))
        print(f"Request:\n{request}")
        print(f"Parameters:\n{parameters}")

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            # print(c.fetchall())
            c.execute(request, parameters)
            results = c.fetchall()
        return results





