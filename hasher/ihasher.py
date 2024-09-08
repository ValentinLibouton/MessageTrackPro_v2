# ihasher.py
# Libraries
from abc import ABC, abstractmethod


class IHasher(ABC):
    @abstractmethod
    def hash_string(self, input_string) -> str:
        pass

    @abstractmethod
    def hash_file(self, file_path: str) -> str:
        pass
