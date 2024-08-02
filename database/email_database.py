import sqlite3


class EmailDatabase:
    def __init__(self, data: dict, db_name='database.db', sql_file='database.sql'):
        self.data = data
        self.db_name = db_name
        self.sql_file = sql_file

    def _create_tables(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        with open(self.sql_file, 'r') as f:
            sql = f.read()
        c.executescript(sql)
        conn.commit()
        conn.close()