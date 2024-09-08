# ifile_retriever.py
# Libraries
from abc import ABC, abstractmethod


class IFileRetriever(ABC):
    """
    FileRetriever is responsible for locating and categorizing files within a specified directory
    or from a single file path. It identifies files based on their extensions and organizes them
    into categories such as email files, mbox files, and unknown files.

    Attributes:
        path (str): The directory or file path to search for files.
        supported_extensions (list, optional): A list of file extensions to consider as supported.
            Defaults to a predefined list of supported email extensions.
        filepath_dict (dict): A dictionary storing file paths categorized by file types.

    Methods:
        retrieve_files_path():
            Initiates the process of traversing the specified directory or file path, identifying
            files, and categorizing them into the filepath_dict.

        filepath_dict:
            Returns the dictionary containing categorized file paths.
    """

    @abstractmethod
    def retrieve_files_path(self) -> None:
        """
        Traverses the specified directory or file path, identifies files based on their extensions,
        and categorizes them into a dictionary.

        If the path is a directory, it recursively traverses the directory tree to locate files. If
        the path is a file, it processes the single file. The identified files are categorized into
        email files, mbox files, and unknown files.

        Raises:
            ValueError: If the path provided is neither a valid directory nor a valid file.
        """
        pass

    @abstractmethod
    def _add_file_to_dict(self, root: str, file: str, single_file=False) -> None:
        """
        Adds a file to the appropriate category in the filepath_dict based on its detected type.

        Args:
            root (str): The root directory of the file.
            file (str): The file name.
            single_file (bool, optional): Indicates whether the file is being processed as a single
                file or part of a directory. Defaults to False.
        """
        pass

    @abstractmethod
    def filepath_dict(self) -> dict:
        """
        Returns the dictionary containing file paths categorized by type.

        Returns:
            dict: A dictionary with keys corresponding to file types (e.g., 'emails', 'mboxes', 'unknowns')
            and values as lists of file paths.
        """
        pass
