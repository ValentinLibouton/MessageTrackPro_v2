import os
from aggregator.file_detector import FileDetector
from aggregator.ifile_retriever import IFileRetriever
from utils.logging_setup import log_file_retriever
from config.file_constants import FileConstants


class FileRetriever(IFileRetriever):
    def __init__(self, path, supported_extensions=None):
        """
        Initializes the FileRetriever with a specified directory or file path and optional supported
        file extensions.

        Args:
            path (str): The directory or file path to search for files.
            supported_extensions (list, optional): A list of file extensions to consider as supported.
                If not provided, it defaults to a predefined list of supported email extensions.

        Raises:
            ValueError: If both path and content are not provided or if both are provided simultaneously.
        """
        self.__path = path
        self.__supported_extensions = supported_extensions if supported_extensions else FileConstants.SUPPORTED_EMAIL_EXTENSIONS
        self.__filepath_dict = {}
        self.file_detector = FileDetector

    def retrieve_files_path(self):
        log_file_retriever.info("Retrieve files path")
        if os.path.isdir(self.__path):
            for root, dirs, files in os.walk(self.__path):
                for file in files:
                    self._add_file_to_dict(root, file)
        elif os.path.isfile(self.__path):
            self._add_file_to_dict(None, os.path.basename(self.__path), single_file=True)
        else:
            raise ValueError(f"{self.__path} is not a valid folder or file")

    def _add_file_to_dict(self, root: str, file: str, single_file=False) -> None:
        if single_file:
            file_path = self.__path
        else:
            file_path = os.path.join(root, file)

        file_type = self.file_detector(file_path).detect_type()

        log_file_retriever.info(f"Add {file_type} file to dictionary - File path: {file_path}")
        if file_type == FileConstants.EMAIL_TYPE:
            self.__filepath_dict.setdefault(FileConstants.EMAILS_KEY, []).append(file_path)
        elif file_type == FileConstants.MBOX_TYPE:
            self.__filepath_dict.setdefault(FileConstants.MBOX_KEY, []).append(file_path)
        elif file_type == FileConstants.UNKNOWN_TYPE:
            self.__filepath_dict.setdefault(FileConstants.UNKNOWN_KEY, []).append(file_path)

    @property
    def filepath_dict(self) -> dict:
        return self.__filepath_dict
