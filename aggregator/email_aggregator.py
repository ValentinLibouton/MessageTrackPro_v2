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

class EmailAggregator:
    def __init__(self, file_retriever: FileRetriever,
                 email_parser: EmailParser,
                 email_database: EmailDatabase,
                 with_attachments=False):
        self._file_retriever = file_retriever
        self._ep = email_parser
        self._db = email_database
        self.retrieve_and_aggregate_emails()

    def retrieve_and_aggregate_emails(self):
        self._file_retriever.retrieve_files_path()
        email_list = self._file_retriever.filepath_dict.get('emails', [])
        mbox_list = self._file_retriever.filepath_dict.get('mbox', [])

        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, Start process email files")
        self.process_email_files(email_list)
        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, End process email files")

        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, Start process mbox files")
        self.process_email_files(mbox_list)
        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, End process mbox files")

    def batch_process(self, items, batch_size, process_func, *args):
        """
        Process items in batches with parallel processing using ProcessPoolExecutor.

        :param items: The list of items to process.
        :param batch_size: The size of each batch.
        :param process_func: The function to process each item.
        :param args: Additional arguments to pass to the processing function.
        :return: A list of results.
        """
        log_email_aggregator.info(f"Func: batch_process, Batch size:{batch_size}, Process func:{process_func}")
        results = []
        batch = []
        with tqdm(total=len(items), desc="Processing items", file=sys.stdout, leave=True) as pbar:
            for item in items:
                batch.append(item)
                if len(batch) >= batch_size:
                    results += self._process_batch(batch, process_func, *args)
                    batch.clear()
                    pbar.update(batch_size)
            if batch:
                results += self._process_batch(batch, process_func, *args)
                pbar.update(len(batch))
        return results

    def _process_batch(self, batch, process_func, *args):
        """
        Helper method to process a batch of items using ProcessPoolExecutor.

        :param batch: The batch of items to process.
        :param process_func: The function to process each item.
        :param args: Additional arguments to pass to the processing function.
        :return: A list of results from the batch.
        """
        log_email_aggregator.info(f"Func: _process_batch, Process func:{process_func}")
        with ProcessPoolExecutor(max_workers=SystemConfig.MAX_WORKERS) as executor:
            futures = [executor.submit(process_func, *item, *args) for item in batch]
            return [future.result() for future in as_completed(futures)]

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

    def add_emails(self, emails):
        self.batch_process(emails, SystemConfig.DEFAULT_BATCH_SIZE, self.add_email)

    def process_email_files_old(self, email_files):
        processed_emails = self.batch_process(email_files, SystemConfig.DEFAULT_BATCH_SIZE, self.process_email_file)
        for file_path, email in processed_emails:
            self.add_email(file_path, email)

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

    def process_mbox_files(self, mbox_files):
        for file_path in mbox_files:
            mbox = mailbox.mbox(file_path)
            emails = []
            for message in mbox:
                # Traiter le message et l'ajouter au batch
                email = self.process_mbox_file(message, file_path)
                emails.append(email)

                # Si le batch atteint la taille définie, traiter les emails
                if len(emails) >= SystemConfig.DEFAULT_BATCH_SIZE:
                    self.add_emails(emails)
                    emails.clear()  # Vider le batch après traitement

            # Traiter les emails restants dans le batch
            if emails:
                self.add_emails(emails)


    def process_email_file(self, file_path):
        with open(file_path, 'rb') as f:
            email_content = f.read()
            # print(f"Fichier: {file_path}")
            email = self._ep.parse_email(email_content=email_content)
            return file_path, email

    def process_mbox_file(self, message, file_path):
        email_content = message.as_bytes()
        email = self._ep.parse_email(email_content=email_content)
        return file_path, email

    @property
    def aggregated_data_dict(self):
        pass
