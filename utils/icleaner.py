from abc import ABC, abstractmethod

class IStringCleaner(ABC):
    @abstractmethod
    def clean(self, string: str) -> str:
        pass

    @abstractmethod
    def split_name_address_from_str(self, fieldvalue: str) -> tuple:
        pass

    @abstractmethod
    def split_names_addresses_from_str(self, fieldvalue: str) -> list:
        pass

    @abstractmethod
    def split_names_addresses_from_list(self, list_of_name_address_tuple: list) -> tuple:
        pass

    @abstractmethod
    def contains_repeated_char(self, string: str, char: str) -> bool:
        pass
