from email.parser import BytesParser
from email.policy import default
import os
import base64
from bs4 import BeautifulSoup
import quopri
import re
import hashlib
import time
import pandas as pd
import mailbox
from tabulate import tabulate


class EmailProcessing:
    def __init__(self, path, with_attachments=False):
        """

        Args:
            path: directory path or file path
        """
        self.__supported_extensions = ('.OUTLOOK.COM', '.eml', '.mbox')
        self.__box_extensions = ('.mbox',)
        self.__filepath_dict = {}
        self.__email_dict = {}
        self.with_attachments = with_attachments
        self.__path = path
        self.__time_for_retrive_file_path = None
        self.__time_for_retrive_contents = None

        #----- Actions -----#
        start = time.time()
        self.__retrieve_files_path()
        self.__file_filtering()

        end = time.time()
        elapsed_time = end - start
        print('Total elapsed Time: ' + str(elapsed_time))

    def __retrieve_files_path(self):
        start_time = time.time()
        if os.path.isdir(self.__path):
            for root, dirs, files in os.walk(self.__path):
                for file in files:
                    self.__add_file_to_dict(root, file)
        elif os.path.isfile(self.__path):
            self.__add_file_to_dict(None, os.path.basename(self.__path), single_file=True)
        else:
            raise ValueError(f"{self.__path} n'est ni un dossier ni un fichier valide.")
        end_time = time.time()
        self.__time_for_retrive_file_path = end_time - start_time


    def __add_file_to_dict(self, root, file, single_file=False):
        if single_file:
            file_path = self.__path
        else:
            file_path = os.path.join(root, file)

        if file.endswith(tuple(self.__supported_extensions)):
            if file.endswith('.OUTLOOK.COM'):
                self.__filepath_dict.setdefault('.OUTLOOK.COM', []).append(file_path)
            elif file.endswith('.eml'):
                self.__filepath_dict.setdefault('.eml', []).append(file_path)
            elif file.endswith('.mbox'):
                self.__filepath_dict.setdefault('.mbox', []).append(file_path)

    def __hash_file(self, filepath):
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()

    def __hash_message(self, msg):
        msg_bytes = msg.as_bytes()
        return hashlib.sha256(msg_bytes).hexdigest()

    def __file_filtering(self):
        start_time = time.time()
        for file_type, filepaths in self.__filepath_dict.items():
            if file_type == ".eml" or file_type == ".OUTLOOK.COM":
                for filepath in filepaths:
                    id, data = self.__extract_email_data(None, filepath=filepath)
                    self.__build_email_dict(id=id, data=data)
            elif file_type == ".mbox":
                for filepath in filepaths:
                    try:
                        mbox = mailbox.mbox(path=filepath)
                        for msg in mbox:
                            id, data = self.__extract_email_data(data=msg, filepath=filepath)
                            self.__build_email_dict(id=id, data=data)
                    except Exception as e:
                        print(f"Error reading mbox file {filepath}: {e}")
            else:
                print("raise NotImplementedError")
        end_time = time.time()
        self.__time_for_retrive_contents = end_time - start_time

    def __extract_email_data(self, data, filepath):
        attachment_names = []
        file_path_attachments = []
        if not data:
            with open(filepath, 'rb') as f:
                msg = BytesParser(policy=default).parse(f)
        else:
            msg = data
        id = self.__hash_message(msg=msg)

        if self.with_attachments:
            pass
        """
        data = {
            'id': id,
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'from': msg['from'],
            'to': msg['to'],
            'cc': msg['cc'] if msg['cc'] else '',
            'bcc': msg['bcc'] if msg['bcc'] else '',
            'subject': msg['subject'],
            'date': msg['date'],
            'body': get_email_content(msg),
            'attachments_names': attachment_names,
            'file_path_attachments': file_path_attachments
        }
        """
        data = {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'from': msg['from'],
            'to': msg['to'],
            'cc': msg['cc'] if msg['cc'] else '',
            'bcc': msg['bcc'] if msg['bcc'] else '',
            'subject': msg['subject'],
            'date': msg['date'],
        }
        return id, data

    def __build_email_dict(self, id, data):
        if id not in self.__email_dict:
            self.__email_dict[id] = []
        self.__email_dict[id].append(data)


    #####################################
    # Fonctionnalités utilisateur
    #####################################
    def get_emails_filepaths(self):
        data = [(file_type, filepath) for file_type, filepaths in self.__filepath_dict.items() for filepath in
                filepaths]
        df = pd.DataFrame(data, columns=['file_type', 'filepath'])
        return df

    def get_emails(self):
        columns = set()
        for infos in self.__email_dict.values():
            for info in infos:
                columns.update(info.keys())
        columns = ['ID'] + list(columns)

        data = []
        for file_id, infos in self.__email_dict.items():
            for info in infos:
                row = {'ID': file_id}
                row.update(info)
                data.append(row)
        df = pd.DataFrame(data, columns=columns)
        return df

    def show_times(self):
        if self.__time_for_retrive_file_path:
            print(f"Execution time of __retrieve_files_path: {self.__time_for_retrive_file_path:.4f} seconds")
        if self.__time_for_retrive_contents:
            print(f"Execution time of __retrive_contents: {self.__time_for_retrive_contents:.4f} seconds")
