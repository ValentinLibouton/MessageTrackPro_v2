import sys
from email.parser import BytesParser
from email.policy import default
import os
import base64
from bs4 import BeautifulSoup
import quopri
import re
import hashlib
import time
from datetime import timedelta
# import pandas as pd
import polars as pl
import mailbox
from tqdm import tqdm
import sys
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
        self.__time_dict = {}
        self.with_attachments = with_attachments
        self.__path = path

        # ----- Actions -----#
        start_time = time.time()
        self.__retrieve_files_path()
        self.__file_processing()
        self.__email_dataframe = self.__build_email_df()

        end_time = time.time()
        self.__time_dict['Total execution time'] = end_time - start_time

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
        self.__time_dict['Time for retrive filepaths'] = end_time - start_time

    def __add_file_to_dict(self, root, file, single_file=False):
        if single_file:
            file_path = self.__path
        else:
            file_path = os.path.join(root, file)

        if file.endswith(tuple(self.__supported_extensions)):
            #print(f"Adding file: {file_path}")
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

    def __file_processing(self):
        start_time = time.time()
        total_files = sum(len(filepaths) for filepaths in self.__filepath_dict.values())
        with tqdm(total=total_files, desc="Processing files", file=sys.stdout, leave=True) as pbar:
            for file_type, filepaths in self.__filepath_dict.items():
                tqdm.write(f"Processing {file_type} files")
                sys.stdout.flush()
                if file_type == ".eml" or file_type == ".OUTLOOK.COM":
                    for filepath in filepaths:
                        id, data = self.__store_email(None, filepath=filepath)
                        self.__build_email_dict(id=id, data=data)
                        pbar.update(1)
                        pbar.refresh()
                        sys.stdout.flush()
                elif file_type == ".mbox":
                    for filepath in filepaths:
                        try:
                            tqdm.write(f"Processing mbox file: {filepath}")
                            sys.stdout.flush()
                            mbox = mailbox.mbox(path=filepath)
                            total_msgs = len(mbox)
                            sys.stdout.flush()
                            for msg in mbox:
                                id, data = self.__store_email(data=msg, filepath=filepath)
                                self.__build_email_dict(id=id, data=data)
                                sys.stdout.flush()
                            pbar.update(1)
                            pbar.refresh()
                            sys.stdout.flush()
                        except Exception as e:
                            tqdm.write(f"Error reading mbox file {filepath}: {e}")
                            sys.stdout.flush()
                else:
                    raise NotImplementedError
                pbar.update(1)
                pbar.refresh()
                sys.stdout.flush()
        end_time = time.time()
        self.__time_dict['Time for file processing'] = end_time - start_time

    def __decode_content(self, part):
        content_type = part.get_content_type()
        content_disposition = part.get("Content-Disposition", None)

        if content_type in ["text/plain", "text/html"] and (
                content_disposition is None or "inline" in content_disposition):
            payload = part.get_payload(decode=True)
            charset = part.get_content_charset() or 'utf-8'  # Use the charset specified in the part, or default to 'utf-8'
            try:
                return payload.decode(charset, errors="replace")
            except LookupError:
                return payload.decode('utf-8', errors="replace")
        return None

    def __store_email(self, data, filepath):
        if not data:
            with open(filepath, 'rb') as f:
                msg = BytesParser(policy=default).parse(f)
        else:
            msg = data
        id = self.__hash_message(msg=msg)

        attachments = []
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue  # Skip multipart container, go deeper
                content = self.__decode_content(part)
                if content:
                    body = content  # Return the first text content found
                if self.with_attachments and part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    content = part.get_payload(decode=True)
                    attachments.append({
                        'filename': filename,
                        'content': content
                    })
        else:
            body = self.__decode_content(msg)

        data = {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'from': msg['from'],
            'to': msg['to'],
            'cc': msg['cc'] if msg['cc'] else '',
            'bcc': msg['bcc'] if msg['bcc'] else '',
            'subject': msg['subject'],
            'date': msg['date'],
            'body': body,
            'attachments': attachments
        }
        return id, data

    def __build_email_dict(self, id, data):
        if id not in self.__email_dict:
            self.__email_dict[id] = []
        self.__email_dict[id].append(data)

    def __build_email_df(self):
        start_time = time.time()
        columns = set()
        for infos in self.__email_dict.values():
            for info in infos:
                columns.update(info.keys())
        data = []
        for file_id, infos in self.__email_dict.items():
            for info in infos:
                row = {'ID': file_id}
                row.update(info)
                data.append(row)
        df = pl.DataFrame(data)
        end_time = time.time()
        self.__time_dict['Time for building email dataframe'] = end_time - start_time
        return df

    # ----- User features -----#

    @property
    def get_emails_filepaths(self):
        data = [(file_type, filepath) for file_type, filepaths in self.__filepath_dict.items() for filepath in
                filepaths]
        df = pl.DataFrame({
            "file_type": [x[0] for x in data],
            "filepath": [x[1] for x in data]
        })
        return df

    def get_emails(self, limit=10):
        return self.__email_dataframe.head(n=limit)

    @property
    def get_duplicates(self):
        raise NotImplementedError

    @property
    def log_execution_time(self):
        if self.__time_dict:
            for text, seconds in self.__time_dict.items():
                elapsed_time = timedelta(seconds=seconds)
                hours, remainder = divmod(elapsed_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                if elapsed_time.days > 0:
                    print(
                        f"{text}: {elapsed_time.days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
                elif hours > 0:
                    print(f"{text}: {hours} hours, {minutes} minutes, {seconds} seconds")
                elif minutes > 0:
                    print(f"{text}: {minutes} minutes, {seconds} seconds")
                else:
                    print(f"{text}: {seconds} seconds")
