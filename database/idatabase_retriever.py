# idatabase_retriever.py
# Libraries
from abc import ABC, abstractmethod
from typing import Self


class IDatabaseRetriever(ABC):

    @abstractmethod
    def validate_arguments(self) -> None:
        pass

    @abstractmethod
    def configure_localization(self, everywhere, words_localization, valid_localizations) -> list:
        pass

    @abstractmethod
    def date_settings(self, start_date: str, end_date: str) -> tuple[int, int]:
        pass

    @abstractmethod
    def select(self) -> Self:
        pass

    @abstractmethod
    def add_join(self, join_clause: str) -> None:
        pass

    @abstractmethod
    def add_where(self, condition: str) -> Self:
        pass

    @abstractmethod
    def add_where_and(self, condition: str) -> Self:
        pass

    @abstractmethod
    def add_order_by(self, columns: list, ascending=True) -> None:
        pass

    @abstractmethod
    def add_limit(self, limit: int) -> Self:
        pass

    @abstractmethod
    def build_query(self) -> str:
        pass

    @abstractmethod
    def join(self) -> Self:
        pass

    @abstractmethod
    def _join_email_addresses(self) -> None:
        pass

    @abstractmethod
    def _join_contacts(self) -> None:
        pass

    @abstractmethod
    def _join_aliases(self) -> None:
        pass

    @abstractmethod
    def _join_dates(self) -> None:
        pass

    @abstractmethod
    def _join_attachments(self) -> None:
        pass

    @abstractmethod
    def where(self) -> Self:
        pass

    @abstractmethod
    def _where_date(self) -> None:
        pass

    @abstractmethod
    def _where_contacts(self) -> None:
        pass

    @abstractmethod
    def _where_aliases(self) -> None:
        pass

    @abstractmethod
    def _where_addresses(self) -> None:
        pass

    @abstractmethod
    def _where_attachments_types(self) -> None:
        pass

    @abstractmethod
    def _where_words(self) -> None:
        pass

    @abstractmethod
    def execute(self, params=None) -> list:
        pass

    @abstractmethod
    def show_query(self) -> str:
        pass
