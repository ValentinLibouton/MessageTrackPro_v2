from abc import ABC, abstractmethod
from typing import Self

class IDatabaseRetriever(ABC):
    @abstractmethod
    def words_localization_control(self) -> None:
        pass

    @abstractmethod
    def date_to_timestamp(self) -> None:
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
    