from abc import ABC, abstractmethod
from typing import Any

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

    @abstractmethod
    def is_empty_var(self, variable: Any) -> bool:
        """
        Checks if the given variable is empty.

        :param variable: The variable to check for emptiness.
        :return: True if the element is empty, False otherwise.
        """
        pass
