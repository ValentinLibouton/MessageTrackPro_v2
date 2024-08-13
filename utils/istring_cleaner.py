from abc import ABC, abstractmethod

class IStringCleaner(ABC):
    @abstractmethod
    def remove_chars(self, string: str) -> str:
        pass

    @abstractmethod
    def contains_repeated_char(self, data, char: str):
        pass

    @abstractmethod
    def to_lower_and_strip(self, data):
        pass

    @abstractmethod
    def replace_chars_by_char(self, fieldvalue, current_chars, new_char: str):
        pass