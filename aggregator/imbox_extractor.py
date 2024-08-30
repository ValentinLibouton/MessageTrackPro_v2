from abc import ABC, abstractmethod
from typing import Iterator, List
from config.system_config import SystemConfig


class ImboxExtractor(ABC):
    """
    Abstract base class for extracting emails from an mbox file. This class defines the
    interface that must be implemented by any concrete class that handles email extraction
    and processing from an mbox file.
    """

    @abstractmethod
    def extract_emails(self, show_progress: bool = True, num_workers: int = SystemConfig.MAX_WORKERS) -> List[str]:
        """
        Abstract method to extract emails from the mbox file and save them to individual files.

        Parameters:
        ----------
        show_progress : bool, optional
            If True, display a progress bar during the extraction process (default is True).

        num_workers : int, optional
            The number of worker processes to use for parallel processing (default is SystemConfig.MAX_WORKERS).

        Returns:
        -------
        List[str]
            A list of file paths to the extracted email files.
        """
        pass

    @staticmethod
    def _count_emails(self, mbox_file_path: str) -> int:
        """
        Counts the total number of emails in the mbox file.

        Parameters:
        ----------
        mbox_file_path : str
            The file path to the mbox file.

        Returns:
        -------
        int
            The total number of emails in the mbox file.
        """
        pass

    @abstractmethod
    def _email_generator(self, mbox_file_path: str) -> Iterator[bytes]:
        """
        Generator function that reads the mbox file line by line and yields each complete email.

        Parameters:
        ----------
        mbox_file_path : str
            The file path to the mbox file.

        Yields:
        ------
        Iterator[bytes]
            An iterator yielding each email as a byte object.
        """
        pass

    @staticmethod
    def _save_email_to_file(byte_email: bytes, file_path: str) -> None:
        """
        Saves the provided email content in bytes to the specified file path.

        Parameters:
        ----------
        byte_email : bytes
            The email content in bytes to be saved.

        file_path : str
            The path where the email content should be saved.

        Returns:
        -------
        None
        """
        pass
