class SQLRequest:
    @staticmethod
    def select_contact_id():
        return "SELECT id FROM Contacts WHERE first_name = ? and last_name = ? "

    @staticmethod
    def select_alias_id():
        return "SELECT id FROM Alias WHERE alias = ?"

    @staticmethod
    def select_email_address_id():
        return "SELECT id FROM EmailAddresses WHERE email_address = ?"

    @staticmethod
    def select_email_id():
        return "SELECT id FROM Email WHERE id = ?"

    @staticmethod
    def select_date_id():
        return "SELECT id FROM Date WHERE date = ?"

    @staticmethod
    def select_timestamp_id():
        return "SELECT id FROM Timestamp WHERE timestamp = ?"






    @staticmethod
    def select_primary_key_from(table, columns):
        placeholders = ', '.join('?' for _ in columns)
        columns_str = ', '.join(columns)
        return f"""SELECT id FROM {table} WHERE ({columns_str}) IN ({placeholders})"""

    def select_table(table, columns):
        #Todo je dois préciser avec ou sans l'id etc...
        placeholders = ', '.join('?' for _ in columns)
        columns_str = ', '.join(columns)
        return f"""SELECT * FROM {table} WHERE ({columns_str}) IN ({placeholders})"""

    @staticmethod
    def insert(table, columns):
        placeholders = ', '.join('?' for _ in columns)
        columns_str = ', '.join(columns)
        return f"""INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})"""

    @staticmethod
    def link(table:str, pk_1:str, pk_2:str):
        return f"INSERT OR IGNORE {table} ({pk_1}, {pk_2}) VALUES (?, ?)"

def list_static_methods(cls):
    import inspect
    static_methods = []
    for name, func in inspect.getmembers_static()