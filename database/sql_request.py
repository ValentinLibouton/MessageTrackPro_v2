# sql_request.py
# Libraries
from typing import List
# Interfaces
from database.isql_request import ISQLRequest


class SQLRequest(ISQLRequest):
    @staticmethod
    def select_primary_key_from(table: str, columns: List[str]) -> str:
        placeholders = ', '.join('?' for _ in columns)
        columns_str = ', '.join(columns)
        return f"""SELECT id FROM {table} WHERE ({columns_str}) IN ({placeholders})"""

    @staticmethod
    def select_table(table: str, columns: List[str]) -> str:
        # Todo je dois préciser avec ou sans l'id etc...?
        placeholders = ', '.join('?' for _ in columns)
        columns_str = ', '.join(columns)
        return f"""SELECT * FROM {table} WHERE ({columns_str}) IN ({placeholders})"""

    @staticmethod
    def insert(table: str, columns: List[str]) -> str:
        placeholders = ', '.join('?' for _ in columns)
        columns_str = ', '.join(columns)
        return f"""INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})"""

    @staticmethod
    def link(table: str, col_name_1: str, col_name_2: str) -> str:
        return f"""INSERT OR IGNORE INTO {table} ({col_name_1}, {col_name_2}) VALUES (?, ?)"""

