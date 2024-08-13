from hasher.ihashable import IHasher
from aggregator.file_retriever import FileRetriever
from parser.email_parser import EmailParser
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import sys




class EmailAggregator:
    def __init__(self, hasher: IHasher, file_retriever: FileRetriever, email_parser: EmailParser, with_attachments=False):
        self.__hasher = hasher
        self.__file_retriever = file_retriever
        self._email_parser = email_parser
        self._email_processor = EmailProcessor(email_parser)
        self.__aggregated_data = {
            'email': set(),         # (email_id, filename, filepath, subject, date_obj, date_iso8601, body)
            'from': set(),    # (email_id, email_address)
            'to': set(),      # (email_id, email_address)
            'cc': set(),      # (email_id, email_address)
            'bcc': set(),     # (email_id, email_address)
            'email_id_attachment_id': set(),  # (email_id, attachment_id)
            'attachments': set()    # (attachment_id, filename, content)


        }
        self.retrieve_and_aggregate_emails()

    def retrieve_and_aggregate_emails(self):
        """
        Récupère et agrège les emails en utilisant FileRetriever.
        """
        self.__file_retriever.retrieve_files_path()
        email_list = self.__file_retriever.filepath_dict.get('emails', [])
        mbox_list = self.__file_retriever.filepath_dict.get('mbox', [])
        self.process_email_files(email_list)
        self.process_email_files(mbox_list)

    def add_email(self, email):
        self.__aggregated_data['from'].add(email['from'])
        self.__aggregated_data['to'].update(email['to'] if email['to'] else set())
        self.__aggregated_data['cc'].update(email['cc'] if email['cc'] else set())
        self.__aggregated_data['bcc'].update(email['bcc'] if email['bcc'] else set())
        #print(self.__aggregated_data)

    def add_emails(self, emails):
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.add_email, email) for email in emails]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Emails aggregation"):
                future.result()

    def hash(self):
        pass


    def process_email_files(self, email_files):
        """
        Traite une liste de fichiers d'emails uniques et les ajoute à l'agrégation.

        Paramètres:
        email_files (list): Liste des chemins des fichiers d'emails.
        """
        total_files = len(email_files)
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.process_email_file, file_path) for file_path in email_files]
            with tqdm(total=total_files, desc="Processing email files", file=sys.stdout, leave=True) as pbar:
                for future in as_completed(futures):
                    email = future.result()
                    self.add_email(email)
                    pbar.update(1)

    def process_mbox_files(self, mbox_files):
        """
        Traite une liste de fichiers mbox contenant plusieurs emails et les ajoute à l'agrégation.

        Paramètres:
        mbox_files (list): Liste des chemins des fichiers mbox.
        """
        import mailbox
        for file_path in mbox_files:
            mbox = mailbox.mbox(file_path)
            emails = []
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self.process_mbox_file, message) for message in mbox]
                with tqdm(total=len(futures), desc=f"Processing mbox: {file_path}", file=sys.stdout, leave=True) as pbar:
                    for future in as_completed(futures):
                        emails.append(future.result())
                        pbar.update(1)
            self.add_emails(emails)


    def process_mbox_files2(self, mbox_files):
        """
        Traite une liste de fichiers mbox contenant plusieurs emails et les ajoute à l'agrégation.

        Paramètres:
        mbox_files (list): Liste des chemins des fichiers mbox.
        """
        import mailbox
        for file_path in mbox_files:
            mbox = mailbox.mbox(file_path)
            emails = []
            for message in tqdm(mbox, desc=f"Processing mbox: {file_path}", file=sys.stdout, leave=True):
                email = self.process_mbox_file(message)
                emails.append(email)
            self.add_emails(emails)

    def process_email_file(self, file_path):
        """
        Traite un fichier d'email unique et l'ajoute à l'agrégation.

        Paramètres:
        file_path (str): Le chemin du fichier d'email.
        """
        with open(file_path, 'rb') as f:
            email_content = f.read()
            email = self._email_parser.parse_email(email_content=email_content)
            return email

    def process_mbox_file(self, message):
        """
        Traite un message mbox et l'ajoute à l'agrégation.

        Paramètres:
        message (mailbox.Message): Le message mbox à traiter.
        """
        email_content = message.as_bytes()
        email = self._email_parser.parse_email(email_content=email_content)
        return email



    @property
    def aggregated_data_dict(self):
        return self.__aggregated_data


class EmailProcessor:
    def __init__(self, email_parser):
        self.email_parser = email_parser

    def process_email_file(self, file_path):
        with open(file_path, 'rb') as f:
            email_content = f.read()
            email = self.email_parser.parse_email(email_content=email_content)
            return email

    def process_mbox_file(self, message):
        email_content = message.as_bytes()
        return self.email_parser.parse_email(email_content=email_content)