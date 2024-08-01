from abc import ABC, abstractmethod

class IFileDetector(ABC):
    @abstractmethod
    def is_email(self) -> bool:
        pass

    @abstractmethod
    def is_mbox(self) -> bool:
        pass

    @abstractmethod
    def detect(self) -> str:
        pass
