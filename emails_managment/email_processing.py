import email.utils
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
import pytz
from datetime import datetime, timedelta
import polars as pl
import mailbox
from tqdm import tqdm
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from tabulate import tabulate


def extract_name_and_email(fieldvalues: str):
    trimmed_field = fieldvalues.strip()
    last_space_index = trimmed_field.rfind(' ')

    if last_space_index == -1:
        address = clean_string(trimmed_field)
        return '', address

    name = trimmed_field[:last_space_index]
    address = trimmed_field[last_space_index + 1:]
    name = clean_string(name)
    address = clean_string(address)
    return name, address



def extract_multiple_names_and_emails(fieldvalues):
    splited_filed = fieldvalues.split(',')
    extracted_list = []
    for field in splited_filed:
        name, email = extract_name_and_email(field)
        d = {'name': name, 'email': email}
        extracted_list.append(d)
    return extracted_list

def is_daylight_saving(date, timezone='Europe/Brussels'):
    tz = pytz.timezone(timezone)
    try:
        localized_date = tz.localize(date, is_dst=None)
    except pytz.AmbiguousTimeError:
        localized_date = tz.localize(date, is_dst=False)
    is_dst = localized_date.dst() != timedelta(0)
    return is_dst

def convert_date_to_datetime(date_str, target_tz="Europe/Brussels"):
    parsed_date = email.utils.parsedate(date_str)
    if parsed_date is None:
        return None
    date_obj = datetime(*parsed_date[:6])

    if is_daylight_saving(date=date_obj): #for Europe/Brussels
        season_offset = 2 * 3600
    else:
        season_offset = 1 * 3600
    time_shift_in_seconds = {
        '+1200': -12 * 3600,
        '+1100': -11 * 3600,
        '+1000': -10 * 3600,
        '+0930': -9.5 * 3600,  # Australia
        '+0900': -9 * 3600,
        '+0845': 8.75 * 3600,  # Australia
        '+0800': -8 * 3600,
        '+0700': -7 * 3600,
        '+0600': -6 * 3600,
        '+0530': -5.5 * 3600,  # India
        '+0500': -5 * 3600,
        '+0400': -4 * 3600,
        '+0300': -3 * 3600,
        '+0200': -2 * 3600,
        '+0100': -1 * 3600,
        '+0000': 0,
        '-0000': 0,
        '-0100': 1 * 3600,
        '-0200': 2 * 3600,
        '-0300': 3 * 3600,
        '-0400': 4 * 3600,
        '-0500': 5 * 3600,
        '-0600': 6 * 3600,
        '-0700': 7 * 3600,
        '-0800': 8 * 3600,
        '-0900': 9 * 3600,
        '-1000': 10 * 3600,
        '-1100': 11 * 3600,
        '-1200': 12 * 3600,

    }
    for substring, offset in time_shift_in_seconds.items():
        if substring in date_str:
            date_obj = date_obj + timedelta(seconds=offset + season_offset)
    target_timezone = pytz.timezone(target_tz)
    date_obj = date_obj.replace(tzinfo=pytz.utc)
    date_obj = date_obj.astimezone(target_timezone)

    return date_obj


def split_names_and_emails(addresses, string_cleaning=True):
    if addresses is None:
        return None, None
    names = []
    emails = []
    for d in addresses:
        name = d.get('name', None)
        email = d.get('email', None)
        """
        if string_cleaning:
            name = clean_string(s=name)
            email = clean_string(s=email)
        """
        names.append(name)
        emails.append(email)
    return names, emails

def clean_string(s):
    if s is None:
        return None
    exclude_char = ['<', '>', '\\', '/', '"', "'"]
    return ''.join([char for char in s if char not in exclude_char])


def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):  # 4 KB chunks
            sha256.update(block)
    return sha256.hexdigest()

def hash_message(data):
    if isinstance(data, bytes):
        msg_bytes = data
    else:
        msg_bytes = data.as_bytes()
    sha256 = hashlib.sha256()
    chunk_size = 8192  # 8 KB chunks
    for i in range(0, len(msg_bytes), chunk_size):
        sha256.update(msg_bytes[i:i + chunk_size])
    return sha256.hexdigest()

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


def has_multiple_at_signs(input_string):
    """
    Check if the input string contains more than one '@' character.

    Parameters:
    input_string (str): The string to be checked.

    Returns:
    bool: True if the string contains more than one '@' character, False otherwise.

    Example:
    >>> has_multiple_at_signs("test@example.com")
    False
    >>> has_multiple_at_signs("test@@example.com")
    True
    """
    return input_string.count('@') > 1


def store_email(data, filepath, with_attachments):
    if not data:
        with open(filepath, 'rb') as f:
            msg = BytesParser(policy=default).parse(f)
    else:
        msg = data
    #----- START to facilitate DB insertions -----#
    all_email_addresses = set()
    all_aliases = set()
    id_email_linked_to_addresses_to = set()
    id_email_linked_to_addresses_cc = set()
    id_email_linked_to_addresses_bcc = set()
    id_email_linked_to_attachments_ids = set()
    # ----- END to facilitate DB insertions -----#
    id = hash_message(data=msg)
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
                if content is not None:
                    id_attachment = hash_message(data=content)
                    id_email_linked_to_attachments_ids.add((id, id_attachment))
                    attachments.append({
                        'id': id_attachment,
                        'filename': filename,
                        'content': content
                    })
    else:
        body = decode_content(msg)
    from_name, from_email = extract_name_and_email(msg['from'])
    to_addresses = extract_multiple_names_and_emails(msg['to']) if msg['to'] else None
    to_names, to_emails = split_names_and_emails(to_addresses)
    cc_addresses = extract_multiple_names_and_emails(msg['cc']) if msg['cc'] else None
    cc_names, cc_emails = split_names_and_emails(cc_addresses)
    bcc_addresses = extract_multiple_names_and_emails(msg['bcc']) if msg['bcc'] else None
    bcc_names, bcc_emails = split_names_and_emails(bcc_addresses)

    all_email_addresses.add(from_email)
    all_email_addresses.update(to_emails)
    all_email_addresses.update(cc_emails)
    all_email_addresses.update(bcc_emails)
    all_aliases.add(from_name)
    all_aliases.update(to_names)
    all_aliases.update(cc_names)
    all_aliases.update(bcc_names)
    id_email_linked_to_addresses_to.update([(id, to) for to in to_emails])
    id_email_linked_to_addresses_cc.update([(id, cc) for cc in cc_emails])
    id_email_linked_to_addresses_bcc.update([(id, bcc) for bcc in bcc_emails])


    # Todo some tests ...
    for txt, type in {'to': to_emails, 'cc': cc_emails, 'bcc': bcc_emails}.items():
        if type:
            for email in type:
                if has_multiple_at_signs(email):
                    print(email)
                    raise ValueError(f"Trop d'adresses dans le champ {txt}:{email}")
    # Todo end of tests

    date_obj = convert_date_to_datetime(msg['date'])
    date_iso8601 = date_obj.isoformat() if date_obj else None
    data = {
        'id': id,
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'from_name': from_name,
        'from_email': from_email,
        'to_names': to_names,
        'to_emails': to_emails,
        # 'cc': msg['cc'],# Todo test en cours
        'cc_name': cc_names,
        'cc_emails': cc_emails,
        'bcc_names': bcc_names,
        'bcc_emails': bcc_emails,
        'subject': msg['subject'],
        'date_obj': date_obj,
        'date_iso8601': date_iso8601,
        'body': body,
        'attachments': attachments,
        # below to facilitate db insertion
        'all_email_addresses': all_email_addresses,
        'all_aliases': all_aliases,
        'id_email_linked_to_addresses_to': id_email_linked_to_addresses_to,
        'id_email_linked_to_addresses_cc': id_email_linked_to_addresses_cc,
        'id_email_linked_to_addresses_bcc': id_email_linked_to_addresses_bcc,
        'id_email_linked_to_attachments_ids': id_email_linked_to_attachments_ids

    }
    return data

def process_file(file_type, filepath, with_attachments):
    email_list = []  # all datas list of dict
    if file_type == ".eml" or file_type == ".OUTLOOK.COM":
        data = store_email(None, filepath=filepath, with_attachments=with_attachments)
        email_list.append(data)  # all datas list of dict
        
    elif file_type == ".mbox":
        try:
            mbox = mailbox.mbox(path=filepath)
            for msg in mbox:
                data = store_email(data=msg, filepath=filepath, with_attachments=with_attachments)
                email_list.append(data)
        except Exception as e:
            print(f"Error reading mbox file {filepath}: {e}")
    else:
        raise NotImplementedError
    return email_list

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
        self.__aggregated_data = {
            'all_email_addresses': set(),
            'all_aliases': set(),
            'id_email_linked_to_addresses_to': set(),
            'id_email_linked_to_addresses_cc': set(),
            'id_email_linked_to_addresses_bcc': set(),
            'id_email_linked_to_attachments_ids': set(),
            'emails': set(),
            'attachments': set()}

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
                    for d in result:
                        self.__aggregated_data['emails'].update((d['id'], d['filepath'], d['filename'],
                                                                 d['from_email'], d['subject'], d['date_obj'],
                                                                 d['date_iso8601'], d['body']))
                        self.__aggregated_data['attachments'].update(d['attachments'])
                        self.__aggregated_data['all_email_addresses'].update(d['all_email_addresses'])
                        self.__aggregated_data['all_aliases'].update(d['all_aliases'])
                        self.__aggregated_data['id_email_linked_to_addresses_to'].update(d['id_email_linked_to_addresses_to'])
                        self.__aggregated_data['id_email_linked_to_addresses_cc'].update(
                            d['id_email_linked_to_addresses_cc'])
                        self.__aggregated_data['id_email_linked_to_addresses_bcc'].update(
                            d['id_email_linked_to_addresses_bcc'])
                        self.__aggregated_data['id_email_linked_to_attachments_ids'].update(d['id_email_linked_to_attachments_ids'])

                        if d['id'] not in self.__email_dict:
                            self.__email_dict[d['id']] = d
                        else:
                            raise NotImplementedError("Duplicate ID found in __file_processing.")

                    pbar.update(1)
                    pbar.refresh()
                    sys.stdout.flush()
        self.__email_list = list(self.__email_dict.values())
        end_time = time.time()
        self.__time_dict['Time for file processing'] = end_time - start_time
        sys.stdout.flush()

    def __build_email_df(self):
        start_time = time.time()
        df = pl.DataFrame(self.__email_list)
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
    def get_emails_list(self):
        return self.__email_list

    def get_aggregated_data(self):
        return self.__aggregated_data


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
