from hasher.ihashable import IHasher
from file_retriever.file_retriever import FileRetriever
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import sys
import time
import os

class EmailAggregator:
    def __init__(self, path, hasher: IHasher, file_retriever: FileRetriever, with_attachments=False):
        self.__hasher = hasher
        self.__file_retriever = file_retriever
        self.__supported_extensions = {'.OUTLOOK.COM', '.eml', '.mbox'}
        self.__filepath_dict = {}
        self.__aggregated_data = {
            'email': set(),         # (email_id, filename, filepath, subject, date_obj, date_iso8601, body)
            'email_from': set(),    # (email_id, email_address)
            'email_to': set(),      # (email_id, email_address)
            'email_cc': set(),      # (email_id, email_address)
            'email_bcc': set(),     # (email_id, email_address)
            'email_id_attachment_id': set(),  # (email_id, attachment_id)
            'attachments': set()    # (attachment_id, filename, content)


        }
        self.path = path

    def file_aggregator(self):
        total_files = 0 # Todo!
        with ProcessPoolExecutor() as executor:
            futures = []
            with tqdm(total=total_files, desc="Processing files", file=sys.stdout, leave=True) as pbar:
