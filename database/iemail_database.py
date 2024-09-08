# iemail_database.py
# Libraries
from abc import ABC, abstractmethod
from typing import Self


class IEmailDatabase(ABC):
    @abstractmethod
    def _create_tables(self) -> None:
        pass

    @abstractmethod
    def insert_contact(self, first_name: str, last_name: str, return_existing_id=False) -> int | None:
        pass

    @abstractmethod
    def insert_alias(self, alias: str, return_existing_id=False) -> int | None:
        pass

    @abstractmethod
    def insert_email_address(self, email_address: str, return_existing_id=False) -> int | None:
        pass

    @abstractmethod
    def insert_email(self, id: str, filepath: str, filename: str, subject: str, body: str) -> str:
        pass

    @abstractmethod
    def insert_date(self, date: str, return_existing_id=False) -> int | None:
        pass

    @abstractmethod
    def insert_timestamp(self, timestamp: int, return_existing_id=False) -> int | None:
        pass

    @abstractmethod
    def insert_attachment(self, id: str, filename: str, content: str, extracted_text: str,
                          return_existing_id=False) -> str:
        pass

    @abstractmethod
    def link(self, table: str, col_name_1: str, col_name_2: str, value_1: int | str, value_2: int | str) -> None:
        pass