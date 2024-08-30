import os
import sys
from tqdm import tqdm
from queue import Queue
from threading import Thread

from config.system_config import SystemConfig
from config.file_constants import FileConstants
from config.db_constants import DBConstants
from config.email_constants import *
from utils.string_cleaner import StringCleaner
from utils.logging_setup import log_email_aggregator_info, log_email_aggregator_debug, log_email_aggregator_error

from aggregator.iemail_aggregator import IEmailAggregator
from aggregator.file_retriever import FileRetriever
from aggregator.mbox_extractor import MboxExtractor
from parser.email_parser import EmailParser
from database.email_database import EmailDatabase


class EmailAggregator(IEmailAggregator):
    def __init__(self, file_retriever: FileRetriever, email_parser: EmailParser, email_database: EmailDatabase,
                 temp_eml_storage_dir: str = None, delete_temp_files: bool = False, with_attachments: bool = False):

        self.temp_dir_name = None
        self.sc = StringCleaner()
        self._file_retriever = file_retriever
        self._ep = email_parser
        self._db = email_database

        self.temp_eml_storage_dir = temp_eml_storage_dir if temp_eml_storage_dir else FileConstants.TEMP_EML_STORAGE_DIR
        self.delete_temp_files = delete_temp_files
        self.with_attachments = with_attachments  # Todo pas encore utilisé, peut-être à supprimer

        self._retrieve_and_process_all_email_types()

    def _retrieve_and_process_all_email_types(self) -> None:
        self._file_retriever.retrieve_files_path()
        email_list = self._file_retriever.filepath_dict().get('emails', [])
        mbox_list = self._file_retriever.filepath_dict().get('mbox', [])

        log_email_aggregator_info.info("Func: retrieve_and_aggregate_emails, Start process mbox files")
        self._process_mbox_files(mbox_list=mbox_list)
        log_email_aggregator_info.info("Func: retrieve_and_aggregate_emails, End process mbox files")

        log_email_aggregator_info.info("Func: retrieve_and_aggregate_emails, Start process email files")
        self._process_email_files(email_files=email_list)
        log_email_aggregator_info.info("Func: retrieve_and_aggregate_emails, End process email files")

    def _aggregate_emails_to_database(self, emails: list) -> None:
        log_email_aggregator_info.info("Start aggregating emails to database")
        self._add_emails(emails=emails)
        log_email_aggregator_info.info("End aggregating emails to database")

    def _process_mbox_files(self, mbox_list: list) -> None:
        for i, mbox_file in enumerate(mbox_list):
            mbox_file_name = self.sc.get_filename_from_path(path=mbox_file, remove_extension_file=True)
            temp_dir_path = self._create_temp_dir(temp_dir=self.temp_eml_storage_dir, sub_dir_name=f"{mbox_file_name}_{i + 1}")
            self._process_mbox_file(mbox_file=mbox_file, temp_dir_path=temp_dir_path)

    def _process_mbox_file(self, mbox_file: str, temp_dir_path: str) -> None:
        log_email_aggregator_debug.debug(f"Func: process_mbox_file: {mbox_file}")
        mbe = MboxExtractor(mbox_file_path=mbox_file, temp_dir=temp_dir_path)
        temp_paths = mbe.extract_emails()
        self._process_email_files(email_files=temp_paths)
        if self.delete_temp_files:
            self._remove_files(paths_list=temp_paths)

    def _process_email_files(self, email_files: list) -> None:
        emails = []
        for email_file in email_files:
            file_path, email = self._process_email_file(file_path=email_file)
            emails.append((file_path, email))
            if len(emails) > SystemConfig.DEFAULT_BATCH_SIZE:
                self._aggregate_emails_to_database(emails=emails)
                emails.clear()
        if emails:
            self._aggregate_emails_to_database(emails=emails)

    def _process_email_file(self, file_path: str) -> tuple[str, dict]:
        with open(file_path, 'rb') as f:
            email_content = f.read()
            email = self._ep.parse_email(email_content=email_content)
            return file_path, email

    def _add_emails(self, emails: list) -> None:
        def worker():
            while True:
                email = q.get()
                if email is None:
                    break
                self._add_email(*email)
                pbar.update(1)
                q.task_done()

        q = Queue()
        num_worker_threads = SystemConfig.MAX_WORKERS
        threads = []
        for i in range(num_worker_threads):
            t = Thread(target=worker)
            t.start()
            threads.append(t)

        with tqdm(total=len(emails), desc="Adding emails", file=sys.stdout, leave=True) as pbar:
            for email in emails:
                q.put(email)

            # block until all tasks are done
            q.join()

            # stop workers
            for i in range(num_worker_threads):
                q.put(None)
            for t in threads:
                t.join()

    def _add_email(self, file_path: str, email: dict) -> None:
        email_id = self._insert_email_record(file_path, email)
        self._insert_aliases(email)
        self._insert_addresses(email, email_id)
        self._insert_dates(email, email_id)
        self._insert_timestamps(email, email_id)
        self._insert_attachments(email, email_id)

    def _remove_files(self, paths_list: list) -> None:
        for file_path in paths_list:
            try:
                os.remove(file_path)
                log_email_aggregator_info.info(f"Deleted temporary file: {file_path}")
            except Exception as e:
                log_email_aggregator_error.error(f"Failed to delete temporary file: {file_path}. Error: {e}")

    def _create_temp_dir(self, temp_dir: str, sub_dir_name: str) -> str:
        if not temp_dir:
            temp_dir = os.getcwd()
        temp_dir_path = os.path.join(temp_dir, sub_dir_name)
        os.makedirs(self.temp_dir_name, exist_ok=True)
        log_email_aggregator_info.info(f"Created directory: {temp_dir_path}")
        return temp_dir_path

    def _insert_email_record(self, file_path: str, email: dict) -> str:
        email_id = self._db.insert_email(
            id=email[EMAIL_ID],
            filepath=file_path,
            filename=os.path.basename(file_path),
            subject=email[SUBJECT],
            body=email[BODY]
        )
        return email_id

    def _insert_aliases(self, email: dict) -> None:
        for name_key in ALL_NAMES:
            for names in email[name_key]:
                if isinstance(names, list) or isinstance(names, tuple) or isinstance(names, set):
                    for name in names:
                        self._db.insert_alias(alias=name)
                elif isinstance(names, str):
                    self._db.insert_alias(alias=names)

    def _insert_addresses(self, email: dict, email_id: str) -> None:
        address_mappings = [
            (DBConstants.EMAIL_FROM_TABLE, DBConstants.EMAIL_FROM_COLUMNS, email[FROM_ADDRESS]),
            (DBConstants.EMAIL_TO_TABLE, DBConstants.EMAIL_TO_COLUMNS, email[TO_ADDRESSES]),
            (DBConstants.EMAIL_CC_TABLE, DBConstants.EMAIL_CC_COLUMNS, email[CC_ADDRESSES]),
            (DBConstants.EMAIL_BCC_TABLE, DBConstants.EMAIL_BCC_COLUMNS, email[BCC_ADDRESSES])
        ]
        for table, columns, addresses in address_mappings:
            ids = [self._db.insert_email_address(email_address=address, return_existing_id=True) for address in addresses]
            self._db.link(table=table, col_name_1=columns[0], col_name_2=columns[1], value_1=email_id, value_2=ids)

    def _insert_dates(self, email: dict, email_id: str) -> None:
        date_str_id = self._db.insert_date(date=email[DATE_STR], return_existing_id=True)
        if date_str_id:
            self._db.link(
                table=DBConstants.EMAIL_DATE_TABLE,
                col_name_1=DBConstants.EMAIL_DATE_COLUMNS[0],
                col_name_2=DBConstants.EMAIL_DATE_COLUMNS[1],
                value_1=email_id, value_2=date_str_id
            )

    def _insert_timestamps(self, email: dict, email_id: str) -> None:
        timestamp_id = self._db.insert_timestamp(timestamp=email[TIMESTAMP], return_existing_id=True)
        if timestamp_id:
            self._db.link(
                table=DBConstants.EMAIL_TIMESTAMP_TABLE,
                col_name_1=DBConstants.EMAIL_TIMESTAMP_COLUMNS[0],
                col_name_2=DBConstants.EMAIL_TIMESTAMP_COLUMNS[1],
                value_1=email_id, value_2=timestamp_id
            )

    def _insert_attachments(self, email: dict, email_id: str) -> None:
        for attachment in email[ATTACHMENTS]:
            attachment_id = attachment[ATTACHMENT_ID]
            self._db.insert_attachment(
                id=attachment_id,
                filename=attachment[ATTACHMENT_FILENAME],
                content=attachment[ATTACHMENT_CONTENT],
                extracted_text=attachment[ATTACHMENT_EXTRACTED_TEXT]
            )
            self._db.link(
                table=DBConstants.EMAIL_ATTACHMENTS_TABLE,
                col_name_1=DBConstants.EMAIL_ATTACHMENTS_COLUMNS[0],
                col_name_2=DBConstants.EMAIL_ATTACHMENTS_COLUMNS[1],
                value_1=email_id, value_2=attachment_id
            )