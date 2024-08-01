from hasher.ihashable import IHasher
from aggregator.file_retriever import FileRetriever
from parser.iemail_parser import IEmailParser
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm


class EmailAggregator:
    def __init__(self, hasher: IHasher, file_retriever: FileRetriever, email_parser: IEmailParser, with_attachments=False):
        self.__hasher = hasher
        self.__file_retriever = file_retriever
        self.__email_parser = email_parser
        self.__aggregated_data = {
            'email': set(),         # (email_id, filename, filepath, subject, date_obj, date_iso8601, body)
            'from': set(),    # (email_id, email_address)
            'to': set(),      # (email_id, email_address)
            'cc': set(),      # (email_id, email_address)
            'bcc': set(),     # (email_id, email_address)
            'email_id_attachment_id': set(),  # (email_id, attachment_id)
            'attachments': set()    # (attachment_id, filename, content)


        }


    def add_email(self, email):
        self.__aggregated_data['from'].add(email['from'])
        print(self.__aggregated_data)

    def add_emails(self, emails):
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.add_email, email) for email in emails]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Emails aggregation"):
                future.result()

    def hash(self):
        pass
    def retrieve_and_aggregate_emails(self):
        """
        Récupère et agrège les emails en utilisant FileRetriever.
        """
        email_list = []
        mbox_list = []
        self.__file_retriever.retrieve_files_path()
        email_list = self.__file_retriever.filepath_dict.get('email', [])
        mbox_list = self.__file_retriever.filepath_dict.get('mbox', [])
        self.process_email_files(email_list)
        self.process_email_files(mbox_list)

    def process_email_files(self, email_files):
        """
        Traite une liste de fichiers d'emails uniques et les ajoute à l'agrégation.

        Paramètres:
        email_files (list): Liste des chemins des fichiers d'emails.
        """
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.process_email_file, file_path) for file_path in email_files]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing email files"):
                future.result()

    def process_mbox_files(self, mbox_files):
        """
        Traite une liste de fichiers mbox contenant plusieurs emails et les ajoute à l'agrégation.

        Paramètres:
        mbox_files (list): Liste des chemins des fichiers mbox.
        """
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.process_mbox_file, file_path) for file_path in mbox_files]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing mbox files"):
                future.result()

    def process_email_file(self, file_path):
        """
        Traite un fichier d'email unique et l'ajoute à l'agrégation.

        Paramètres:
        file_path (str): Le chemin du fichier d'email.
        """
        with open(file_path, 'r') as f:
            email_content = f.read()
            email = self.__email_parser.parse_email(email_content)
            self.add_email(email)

    def process_mbox_file(self, file_path):
        """
        Traite un fichier mbox contenant plusieurs emails et les ajoute à l'agrégation.

        Paramètres:
        file_path (str): Le chemin du fichier mbox.
        """
        import mailbox
        mbox = mailbox.mbox(file_path)
        emails = []
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.__email_parser.parse_email, message.as_bytes()) for message in mbox]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing mbox: {file_path}"):
                emails.append(future.result())
        self.add_emails(emails)


    @property
    def aggregated_data_dict(self):
        return self.__aggregated_data
