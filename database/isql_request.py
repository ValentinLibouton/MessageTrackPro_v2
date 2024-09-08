# isql_request.py
# Libraries
from typing import List
class ISQLRequest:
    @staticmethod
    def select_primary_key_from(table: str, columns: List[str]) -> str:
        pass

    @staticmethod
    def select_table(table: str, columns: List[str]) -> str:
        pass

    @staticmethod
    def insert(table: str, columns: List[str]) -> str:
        pass

    @staticmethod
    def link(table: str, col_name_1: str, col_name_2: str) -> str:
        pass