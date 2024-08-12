from abc import ABC, abstractmethod

class IStringCleaner(ABC):
    @abstractmethod
    def remove_chars(self, string: str) -> str:
        pass

    @abstractmethod
    def split_name_address(self, fieldvalue: str) -> list:
        pass

    @abstractmethod
    def separate_names_and_addresses_from_list(self, list_of_name_address_tuple: list) -> tuple:
        pass

    @abstractmethod
    def contains_repeated_char(self, string: str, char: str) -> bool:
        pass

    @abstractmethod
    def to_lower_and_trim(self, string: str) -> str:
        pass

    @abstractmethod
    def replace_chars_by_char(self, fieldvalue, current_chars, new_char: str):
        pass