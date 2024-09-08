# ifile_detector.py
# Libraries
from abc import ABC, abstractmethod


class IFileDetector(ABC):
    """
    Interface for detecting file types.

    Methods:
        is_email() -> bool:
            Determines if the file is an email based on its extension or content.
        is_mbox() -> bool:
            Determines if the file is an mbox archive.
        detect_type() -> str:
            Detects the type of the file ('email', 'mbox', or 'unknown').
    """

    @abstractmethod
    def is_email(self) -> bool:
        """Determines if the file is an email based on its extension or content."""
        pass

    @abstractmethod
    def is_mbox(self) -> bool:
        """Determines if the file is an mbox archive."""
        pass

    @abstractmethod
    def detect_type(self) -> str:
        """Detects the type of the file ('email', 'mbox', or 'unknown')."""
        pass
