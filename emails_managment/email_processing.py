import sys
from email.parser import BytesParser
from email.policy import default
import os
import base64
from bs4 import BeautifulSoup
import quopri
import re
from email.utils import parseaddr, getaddresses
import hashlib
import time
from datetime import timedelta
# import pandas as pd
import polars as pl
import mailbox
from tqdm import tqdm
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from tabulate import tabulate

def extract_name_and_email(email_str):
    name, email = parseaddr(email_str)
    return name, email

def extract_multiple_names_and_emails(email_str):
    addresses = getaddresses([email_str])
    return [{'name': name, 'email': email} for name, email in addresses]

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            sha256.update(block)
    return sha256.hexdigest()

def hash_message(msg):
    msg_bytes = msg.as_bytes()
    return hashlib.sha256(msg_bytes).hexdigest()

def decode_content(part):
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


def store_email(data, filepath, with_attachments):
    if not data:
        with open(filepath, 'rb') as f:
            msg = BytesParser(policy=default).parse(f)
    else:
        msg = data
    id = hash_message(msg=msg)

    attachments = []
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue  # Skip multipart container, go deeper
            content = decode_content(part)
            if content:
                body = content  # Return the first text content found
            if with_attachments and part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                content = part.get_payload(decode=True)
                attachments.append({
                    'filename': filename,
                    'content': content
                })
    else:
        body = decode_content(msg)
    from_name, from_email = extract_name_and_email(msg['from'])
    to_addresses = extract_multiple_names_and_emails(msg['to']) if msg['to'] else []
    cc_addresses = extract_multiple_names_and_emails(msg['cc']) if msg['cc'] else []
    bcc_addresses = extract_multiple_names_and_emails(msg['bcc']) if msg['bcc'] else []

    data = {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'from': msg['from'],
        'from_name': from_name,
        'from_email': from_email,
        'to': msg['to'],
        'to_splited': to_addresses,
        'cc': msg['cc'] if msg['cc'] else '',
        'cc_splited': cc_addresses,
        'bcc': msg['bcc'] if msg['bcc'] else '',
        'bcc_splited': bcc_addresses,
        'subject': msg['subject'],
        'date': msg['date'],
        'body': body,
        'attachments': attachments
    }
    return id, data

def process_file(file_type, filepath, with_attachments):
    email_dict = {}
    if file_type == ".eml" or file_type == ".OUTLOOK.COM":
        id, data = store_email(None, filepath=filepath, with_attachments=with_attachments)
        email_dict[id] = [data]
    elif file_type == ".mbox":
        try:
            mbox = mailbox.mbox(path=filepath)
            for msg in mbox:
                id, data = store_email(data=msg, filepath=filepath, with_attachments=with_attachments)
                if id not in email_dict:
                    email_dict[id] = []
                email_dict[id].append(data)
        except Exception as e:
            print(f"Error reading mbox file {filepath}: {e}")
    else:
        raise NotImplementedError
    return email_dict

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

    def __file_processing(self):
        start_time = time.time()
        total_files = sum(len(filepaths) for filepaths in self.__filepath_dict.values())

        with ProcessPoolExecutor() as executor:
            futures = []
            with tqdm(total=total_files, desc="Processing files", file=sys.stdout, leave=True) as pbar:
                for file_type, filepaths in self.__filepath_dict.items():
                    for filepath in filepaths:
                        futures.append(executor.submit(process_file, file_type, filepath, self.with_attachments))

                for future in as_completed(futures):
                    result = future.result()
                    for id, data in result.items():
                        if id not in self.__email_dict:
                            self.__email_dict[id] = []
                        self.__email_dict[id].extend(data)
                    pbar.update(1)
                    pbar.refresh()
                    sys.stdout.flush()

        end_time = time.time()
        self.__time_dict['Time for file processing'] = end_time - start_time
        sys.stdout.flush()

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
