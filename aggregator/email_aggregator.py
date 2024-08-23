from constants import SystemConfig
from hasher.ihashable import IHasher
from aggregator.file_retriever import FileRetriever
from parser.email_parser import EmailParser
from database.email_database import EmailDatabase
from utils.system_monitor import SystemMonitor
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import sys
import os
import psutil
import mailbox
from utils.log import log_email_aggregator
from aggregator.mbox_extractor import MboxExtractor


class EmailAggregator:
    def __init__(self, file_retriever: FileRetriever,
                 email_parser: EmailParser,
                 email_database: EmailDatabase,
                 mbox_temp_directory: str = None,
                 with_attachments: bool = False,
                 delete_temp_files: bool = False):
        self.temp_dir_name = None
        self._file_retriever = file_retriever
        self._ep = email_parser
        self._db = email_database
        self.delete_temp_files = delete_temp_files
        self.mbox_temp_directory = mbox_temp_directory
        self.retrieve_and_aggregate_emails()
        self.with_attachments = with_attachments  #Todo pas encore utilisé, peut-être à supprimer


    def retrieve_and_aggregate_emails(self):
        self._file_retriever.retrieve_files_path()
        email_list = self._file_retriever.filepath_dict.get('emails', [])
        mbox_list = self._file_retriever.filepath_dict.get('mbox', [])

        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, Start process mbox files")
        self.process_mbox_files(mbox_list=mbox_list)
        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, End process mbox files")

        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, Start process email files")
        self.process_email_files(email_files=email_list)
        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, End process email files")

    def process_mbox_files(self, mbox_list):
        for i, mbox_file in enumerate(mbox_list):
            self.create_temp_dir(temp_dir=self.mbox_temp_directory, sub_dir_name=f"mbox_temp_{i + 1}")
            self.process_mbox_file(mbox_file=mbox_file)

    def process_mbox_file(self, mbox_file):
        mbe = MboxExtractor(mbox_file_path=mbox_file, temp_dir=self.temp_dir_name)
        temp_paths = mbe.extract_emails()
        self.process_email_files(email_files=temp_paths)
        if self.delete_temp_files:
            self.remove_files(paths_list=temp_paths)

    def process_email_files(self, email_files):
        emails = []
        for email_file in email_files:
            file_path, email = self.process_email_file(file_path=email_file)
            emails.append((file_path, email))
            if len(emails) > SystemConfig.DEFAULT_BATCH_SIZE:
                self.add_emails(emails)
                emails.clear()
        if emails:
            self.add_emails(emails)

    def process_email_file(self, file_path):
        with open(file_path, 'rb') as f:
            email_content = f.read()
            # print(f"Fichier: {file_path}")
            email = self._ep.parse_email(email_content=email_content)
            return file_path, email

    def add_emails(self, emails):
        with ProcessPoolExecutor(max_workers=SystemConfig.MAX_WORKERS) as executor:
            futures = []
            with tqdm(total=len(emails), desc="Adding emails", file=sys.stdout, leave=True) as pbar:
                for email in emails:
                    future = executor.submit(self.add_email, *email)
                    futures.append(future)

                for future in as_completed(futures):
                    future.result()  # To raise any exceptions
                    pbar.update(1)

    def add_email(self, file_path, email):
        email_id = self._db.insert_email(id=email['email_id'],
                                         filepath=file_path,
                                         filename=os.path.basename(file_path),
                                         subject=email['subject'],
                                         body=email['body'])

        for names in [email['from_name'], email['to_names'], email['cc_names'], email['bcc_names']]:
            [self._db.insert_alias(alias=name) for name in names]

        id_from = [self._db.insert_email_address(email_address=address,
                                                 return_existing_id=True) for address in email['from_address']]
        self._db.link(table='Email_From', col_name_1='email_id', col_name_2='email_address_id',
                      value_1=email_id, value_2=id_from)

        id_to = [self._db.insert_email_address(email_address=address,
                                               return_existing_id=True) for address in email['to_addresses']]
        self._db.link(table='Email_To', col_name_1='email_id', col_name_2='email_address_id',
                      value_1=email_id, value_2=id_to)

        id_cc = [self._db.insert_email_address(email_address=address,
                                               return_existing_id=True) for address in email['cc_addresses']]
        self._db.link(table='Email_Cc', col_name_1='email_id', col_name_2='email_address_id',
                      value_1=email_id, value_2=id_cc)

        id_bcc = [self._db.insert_email_address(email_address=address,
                                                return_existing_id=True) for address in email['bcc_addresses']]
        self._db.link(table='Email_Bcc', col_name_1='email_id', col_name_2='email_address_id',
                      value_1=email_id, value_2=id_bcc)

        date_str_id = self._db.insert_date(date=email['date_str'], return_existing_id=True)
        self._db.link(table='Email_Date', col_name_1='email_id', col_name_2='date_id',
                      value_1=email_id, value_2=date_str_id)

        timestamp_id = self._db.insert_timestamp(timestamp=email['timestamp'], return_existing_id=True)
        self._db.link(table='Email_Timestamp', col_name_1='email_id', col_name_2='timestamp_id',
                      value_1=email_id, value_2=timestamp_id)

        for attachment in email['attachments']:
            attachment_id = attachment['attachment_id']
            self._db.insert_attachment(id=attachment_id, filename=attachment['filename'],
                                       content=attachment['content'], extracted_text=attachment['extracted_text'])
            self._db.link(table='Email_Attachments', col_name_1='email_id', col_name_2='attachment_id',
                          value_1=email_id, value_2=attachment_id)

    def remove_files(self, paths_list):
        for file_path in paths_list:
            try:
                os.remove(file_path)
                log_email_aggregator.info(f"Deleted temporary file: {file_path}")
            except Exception as e:
                log_email_aggregator.error(f"Failed to delete temporary file: {file_path}. Error: {e}")

    def create_temp_dir(self, temp_dir, sub_dir_name):
        if not temp_dir:
            temp_dir = os.getcwd()
        self.temp_dir_name = os.path.join(temp_dir, sub_dir_name)
        os.makedirs(self.temp_dir_name, exist_ok=True)
        log_email_aggregator.info(f"Created directory: {self.temp_dir_name}")
