class SQLRequest:
    @staticmethod
    def select_primary_key_from(table, columns):
        placeholders = ', '.join('?' for _ in columns)
        columns_str = ', '.join(columns)
        return f"""SELECT id FROM {table} WHERE ({columns_str}) IN ({placeholders})"""

    @staticmethod
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
    for name, member in inspect.getmembers_static(cls):
        if isinstance(member, staticmethod):
            static_methods.append(name)
    return static_methods

if __name__ == '__main__':
    static_methods = list_static_methods(SQLRequest)
    print("Static methods:", static_methods)