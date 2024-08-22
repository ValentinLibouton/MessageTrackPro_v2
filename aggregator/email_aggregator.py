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
import tempfile
from aggregator.mbox_email_streamer import MboxEmailStreamer

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

        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, Start process mbox files")
        self.process_email_files(mbox_list)
        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, End process mbox files")

        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, Start process email files")
        self.process_email_files(email_list)
        log_email_aggregator.info("Func: retrieve_and_aggregate_emails, End process email files")



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

    def process_mbox_files_old(self, mbox_files):
        for file_path in mbox_files:
            mbox = mailbox.mbox(file_path)
            emails = []
            with tqdm(total=len(mbox), desc=f"Processing mbox: {os.path.basename(file_path)}", file=sys.stdout,
                      leave=True) as pbar:
                for message in mbox:
                    file_path, email = self.process_message_from_mbox_file(message, file_path)
                    emails.append((file_path, email))

                    # If the batch reaches the size defined in SystemConfig, process the emails
                    if len(emails) >= SystemConfig.DEFAULT_BATCH_SIZE:
                        self.add_emails(emails)
                        emails.clear()  # Clear the batch after processing
                        pbar.update(SystemConfig.DEFAULT_BATCH_SIZE)

                # Process any remaining emails in the batch
                if emails:
                    self.add_emails(emails)
                    pbar.update(len(emails))

    def process_mbox_files(self, mbox_files):
        log_email_aggregator.info("Func: process_mbox_files")
        for mbox_file in mbox_files:
            # Créer une instance de MboxEmailStreamer pour le fichier mbox
            streamer = MboxEmailStreamer(mbox_file)

            def process_single_email(email_message):
                """
                Fonction de traitement pour un seul email.
                """
                email_content = email_message.as_bytes()
                email = self._ep.parse_email(email_content=email_content)
                self.add_email(mbox_file, email)

            # Utilisation de la fonction de traitement
            streamer.process_emails(process_single_email, show_progress=True)

    def process_message_from_mbox_file(self, message, file_path):
        email_content = message.as_bytes()
        email = self._ep.parse_email(email_content=email_content)
        return file_path, email

    def process_large_mbox_to_eml(self, mbox_file):
        log_email_aggregator.info("Func: process_large_mbox_to_eml")
        temp_dir = tempfile.mkdtemp()  # Create a temporary directory for eml files

        with open(mbox_file, 'rb') as f:
            mbox = mailbox.UnixMailbox(f, factory=mailbox.mboxMessage)

            for i, message in enumerate(mbox):
                log_email_aggregator.info(f"Func: process_large_mbox_to_eml, element n°{i}")
                temp_eml_path = os.path.join(temp_dir, f'email_{i}.eml')
                with open(temp_eml_path, 'wb') as eml_file:
                    eml_file.write(message.as_bytes())

                # Process the individual eml file
                self.process_email_files([temp_eml_path])

                # Delete the temporary eml file after processing
                os.remove(temp_eml_path)