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
    def link(table, col_name_1, col_name_2):
        return f"""INSERT OR IGNORE INTO {table} ({col_name_1}, {col_name_2}) VALUES (?, ?)"""

    @staticmethod
    def simple_word_search(table, columns):
        request = f"""SELECT id FROM {table} WHERE LOWER({columns[0]}) LIKE '%' || LOWER(?) || '%'"""
        if len(columns) > 1:
            for column in columns[1:]:
                request += f""" OR LOWER({column}) LIKE '%' || LOWER(?) || '%'"""
        return request

    @staticmethod
    def all_words_search(table, columns, words):
        """
        Generates an SQL query that selects the primary key from a specified table
        where all of the given words must appear in at least one of the specified columns.

        Parameters:
        - table (str): The name of the table to search within.
        - columns (list): A list of column names to search within.
        - words (list): A list of words that must all be present in the specified columns.

        Returns:
        - str: An SQL query string that checks if all the specified words are present
               in the specified columns. The query uses case-insensitive matching.

        Example:
        >>> SQLRequest.all_words_search('Emails', ['subject', 'body'], ['urgent', 'meeting'])
        "SELECT id FROM Emails WHERE
        (LOWER(subject) LIKE '%' || LOWER(?) || '%' OR LOWER(body) LIKE '%' || LOWER(?) || '%') AND
        (LOWER(subject) LIKE '%' || LOWER(?) || '%' OR LOWER(body) LIKE '%' || LOWER(?) || '%')"
        """
        request = f"""SELECT id FROM {table} WHERE """
        conditions = []

        for word in words:
            word_conditions = []
            for column in columns:
                word_conditions.append(f"LOWER({column}) LIKE '%' || LOWER(?) || '%'")
            conditions.append(f"({' OR '.join(word_conditions)})")

        request += " AND ".join(conditions)
        return request

    @staticmethod
    def any_word_search(table, columns, words, ids=None):
        """
        Generates an SQL query that selects the primary key from a specified table
        where any of the given words must appear in at least one of the specified columns.

        Parameters:
        - table (str): The name of the table to search within.
        - columns (list): A list of column names to search within.
        - words (list): A list of words where at least one must be present in the specified columns.

        Returns:
        - str: An SQL query string that checks if at least one of the specified words
               is present in the specified columns. The query uses case-insensitive matching.

        Example:
        >>> SQLRequest.any_word_search('Emails', ['subject', 'body'], ['urgent', 'meeting'])
        "SELECT id FROM Emails WHERE
        (LOWER(subject) LIKE '%' || LOWER(?) || '%' OR LOWER(body) LIKE '%' || LOWER(?) || '%') OR
        (LOWER(subject) LIKE '%' || LOWER(?) || '%' OR LOWER(body) LIKE '%' || LOWER(?) || '%')"
        """
        request = f"""SELECT id FROM {table} WHERE """
        word_conditions = []

        for word in words:
            column_conditions = " OR ".join([f"LOWER({column}) LIKE '%' || LOWER(?) || '%'" for column in columns])
            word_conditions.append(f"({column_conditions})")

        request += " OR ".join(word_conditions)

        if ids:
            id_conditions = ", ".join([id for id in ids])
            request += f" AND id IN ({id_conditions})"
        return request



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