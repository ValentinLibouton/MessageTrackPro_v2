# iemail_aggregator.py
# Libraries
from abc import ABC, abstractmethod


class IEmailAggregator(ABC):
    """
    Interface for the EmailAggregator class, providing methods to retrieve, process, and aggregate email data into a database.
    """

    @abstractmethod
    def _retrieve_and_process_all_email_types(self) -> None:
        """
        Retrieve and process all email types, including individual email files and mbox files.
        The processed emails are stored in a database.
        """
        pass

    @abstractmethod
    def _aggregate_emails_to_database(self, emails: list) -> None:
        """
        Aggregate a list of emails into the database.

        :param emails: A list of email data to be aggregated into the database.
        """
        pass

    @abstractmethod
    def _process_mbox_files(self, mbox_list: list) -> None:
        """
        Process a list of mbox files, extracting individual emails and storing them in a database.

        :param mbox_list: A list of mbox file paths to be processed.
        """
        pass

    @abstractmethod
    def _process_mbox_file(self, mbox_file: str, temp_dir_path: str) -> None:
        """
        Process a single mbox file, extract emails, and store them in a database.

        :param mbox_file: Path to the mbox file to be processed.
        :param temp_dir_path: Path to the temporary directory where extracted emails will be stored.
        """
        pass

    @abstractmethod
    def _process_email_files(self, email_files: list) -> None:
        """
        Process a list of email files, extracting relevant information and storing it in a database.

        :param email_files: A list of email file paths to be processed.
        """
        pass

    @abstractmethod
    def _process_email_file(self, file_path: str) -> tuple[str, dict]:
        """
        Process a single email file, extracting relevant information and returning it as a dictionary.

        :param file_path: Path to the email file to be processed.
        :return: A tuple containing the file path and a dictionary of the extracted email data.
        """
        pass

    @abstractmethod
    def _add_emails(self, emails: list) -> None:
        """
        Add a list of emails to the database using a multi-threaded approach for efficiency.

        :param emails: A list of email data to be added to the database.
        """
        pass

    @abstractmethod
    def _add_email(self, file_path: str, email: dict) -> None:
        """
        Add a single email to the database, handling insertion of email metadata, addresses, dates, timestamps, and attachments.

        :param file_path: Path to the email file.
        :param email: A dictionary containing the email data to be added to the database.
        """
        pass

    @abstractmethod
    def _remove_files(self, paths_list: list) -> None:
        """
        Remove a list of temporary files from the file system.

        :param paths_list: A list of file paths to be removed.
        """
        pass

    @abstractmethod
    def _create_temp_dir(self, temp_dir: str, sub_dir_name: str) -> str:
        """
        Create a temporary directory for storing intermediate files, such as extracted emails.

        :param temp_dir: Base directory where the temporary directory will be created.
        :param sub_dir_name: Name of the subdirectory to be created within the base directory.
        :return: The full path to the created temporary directory.
        """
        pass

    @abstractmethod
    def _insert_email_record(self, file_path: str, email: dict) -> str:
        """
        Insert an email record into the database.

        :param file_path: Path to the email file.
        :param email: A dictionary containing the email data to be inserted.
        :return: The ID of the inserted email record.
        """
        pass

    @abstractmethod
    def _insert_aliases(self, email: dict) -> None:
        """
        Insert alias data from the email into the database.

        :param email: A dictionary containing the email data with aliases to be inserted.
        """
        pass

    @abstractmethod
    def _insert_addresses(self, email: dict, email_id: str) -> None:
        """
        Insert email addresses into the database and link them to the given email ID.

        :param email: A dictionary containing the email data with addresses to be inserted.
        :param email_id: The ID of the email record to which the addresses should be linked.
        """
        pass

    @abstractmethod
    def _insert_dates(self, email: dict, email_id: str) -> None:
        """
        Insert date information from the email into the database and link it to the given email ID.

        :param email: A dictionary containing the email data with dates to be inserted.
        :param email_id: The ID of the email record to which the dates should be linked.
        """
        pass

    @abstractmethod
    def _insert_timestamps(self, email: dict, email_id: str) -> None:
        """
        Insert timestamp information from the email into the database and link it to the given email ID.

        :param email: A dictionary containing the email data with timestamps to be inserted.
        :param email_id: The ID of the email record to which the timestamps should be linked.
        """
        pass

    @abstractmethod
    def _insert_attachments(self, email: dict, email_id: str) -> None:
        """
        Insert attachment information from the email into the database and link it to the given email ID.

        :param email: A dictionary containing the email data with attachments to be inserted.
        :param email_id: The ID of the email record to which the attachments should be linked.
        """
        pass