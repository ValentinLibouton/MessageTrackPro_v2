from hasher.ihashable import IHasher
from aggregator.file_retriever import FileRetriever
from parser.email_parser import EmailParser
from database.email_database import EmailDatabase
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import sys
import os


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
        self.process_email_files(email_list)
        self.process_email_files(mbox_list)

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
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.add_email, email) for email in emails]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Emails aggregation"):
                future.result()

    def process_email_files(self, email_files):
        total_files = len(email_files)
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.process_email_file, file_path) for file_path in email_files]
            with tqdm(total=total_files, desc="Processing email files", file=sys.stdout, leave=True) as pbar:
                for future in as_completed(futures):
                    email = future.result()
                    self.add_email(*email)
                    pbar.update(1)

    def process_mbox_files(self, mbox_files):
        import mailbox
        for file_path in mbox_files:
            mbox = mailbox.mbox(file_path)
            emails = []
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self.process_mbox_file, message, file_path) for message in mbox]
                with tqdm(total=len(futures), desc=f"Processing mbox: {file_path}", file=sys.stdout,
                          leave=True) as pbar:
                    for future in as_completed(futures):
                        emails.append(future.result())
                        pbar.update(1)
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
