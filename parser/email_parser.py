import gc
import os
from email import policy
from email.parser import BytesParser
import mailbox
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Union, Any

from config.email_parser_constants import EmailParserConstants
from config.email_constants import *
from utils.file_text_extractor import FileTextExtractor

from .iemail_parser import IEmailParser
from utils.string_cleaner import StringCleaner
from utils.date_transformer import DateTransformer
from utils.logging_setup import log_email_parser
from hasher.hasher import Hasher


class EmailParser(IEmailParser):
    def __init__(self, attachments_directory=None):
        self.sc = StringCleaner()
        self.dt = DateTransformer()
        self.hasher = Hasher()
        if attachments_directory:
            self.attachments_directory = attachments_directory
        else:
            self.attachments_directory = EmailParserConstants.ATTACHMENTS_DIRECTORY

    def parse_email(self, email_content: bytes) -> dict:
        """
        Analyse le contenu d'un email et retourne un dictionnaire avec les données pertinentes.

        Paramètres:
        email_content (bytes): Le contenu de l'email en bytes.

        Retourne:
        dict: Un dictionnaire contenant les données de l'email.
        """
        log_email_parser.info("Func: parse_email")
        msg = BytesParser(policy=policy.default).parsebytes(email_content)
        email_id = self.hasher.hash_string(data=msg.as_bytes())
        log_email_parser.debug(f"Func: parse_email for email_id: {email_id}")
        date = self._transform_date(msg['date'])
        log_email_parser.debug(f"Func: parse_email with date: {date}")
        body, attachments = self.extract_body_and_attachments(msg=msg)

        from_name, from_address = self._parse_names_addresses(data=msg['from'])
        to_names, to_addresses = self._parse_names_addresses(data=msg['to'])
        cc_names, cc_addresses = self._parse_names_addresses(data=msg['cc'])
        bcc_names, bcc_addresses = self._parse_names_addresses(data=msg['bcc'])

        return {
            EMAIL_ID: email_id,
            FROM_NAME: from_name,
            FROM_ADDRESS: from_address,
            SUBJECT: msg['subject'],
            DATE_STR: date.strftime(DATETIME_FORMAT) if date else None,
            DATE_OBJ: date if date else None,
            DATE_ISO: date.isoformat() if date else None,
            TIMESTAMP: date.timestamp() if date else None,
            TO_NAMES: to_names,
            TO_ADDRESSES: to_addresses,
            CC_NAMES: cc_names,
            CC_ADDRESSES: cc_addresses,
            BCC_NAMES: bcc_names,
            BCC_ADDRESSES: bcc_addresses,
            BODY: body,
            ATTACHMENTS: attachments
        }

    def extract_body_and_attachments(self, msg: BytesParser) -> Tuple[Optional[str], List[Dict[str, Union[str, bytes]]]]:
        log_email_parser.info("Func: extract_body_and_attachments")
        body = None
        attachments = []
        for part in msg.walk():
            content_disposition = part.get('Content-Disposition')
            if part.get_content_maintype() == 'multipart':
                continue  # Skip multipart container, go deeper
            elif content_disposition is None:
                # This is the email body
                if part.get_content_type() in ["text/plain", "text/html"]:
                    charset = part.get_content_charset()
                    if charset:
                        try:
                            # Attempt to decode with the specified charset
                            body_content = part.get_payload(decode=True).decode(charset)
                        except (LookupError, UnicodeDecodeError):
                            # Fallback to utf-8 if charset is unknown or decoding fails
                            log_email_parser.warning(
                                f"Unknown or invalid charset '{charset}', falling back to 'utf-8'.")
                            body_content = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    else:
                        # No charset specified, default to utf-8
                        body_content = part.get_payload(decode=True).decode('utf-8', errors='replace')

                    if part.get_content_type() == "text/plain" or body is None:
                        body = body_content

            elif "attachment" in content_disposition:
                log_email_parser.info("Func: extract_body_and_attachments, attachment found.")
                # This is an attachment
                filename = part.get_filename()
                content = part.get_payload(decode=True)
                if content is not None:
                    attachment_id = self.hasher.hash_string(data=content)
                    log_email_parser.debug(f"Func: extract_body_and_attachments, attachment_id: {attachment_id}")
                    filepath = self._download_attachment(content=content, attachment_id=attachment_id, filename=filename)
                    file_text_extractor = FileTextExtractor(file_path=filepath)
                    extracted_text = file_text_extractor.extract_text()
                    attachments.append({
                        'attachment_id': attachment_id,
                        'filename': filename,
                        'content': content,
                        'extracted_text': extracted_text  # Todo: tests à faire !
                    })
                    del content
                    gc.collect()
                else:
                    # Handle the case where content is None
                    print(f"Warning: Attachment {filename} has no content and was skipped.")
        return body, attachments

    def _download_attachment(self, content: Any, attachment_id: str, filename: str) -> None:
        try:
            self.sc.create_directory(dir_path=self.attachments_directory)
            new_filename = self.sc.rename_file(filename=filename, new_name=attachment_id)
            filepath = os.path.join(self.attachments_directory, new_filename)
            if not self.sc.file_exists(filepath):
                log_email_parser.info(f"Download attachment {filepath}")
                with open(filepath, 'wb') as f:
                    f.write(content)
            else:
                log_email_parser.debug(f"Attachment {filename} already exists")
            return filepath
        except Exception as e:
            raise Exception(f"{filename}: {e}")

    def _parse_names_addresses(self, data: str) -> Tuple[List[str], List[str]]:
        # log_email_parser.info("Func: _parse_names_addresses")
        list_names_and_addresses = self.split_name_address(fieldvalue=data)
        names, addresses = self.separate_names_and_addresses_from_list(list_names_and_addresses)
        names = self.sc.replace_chars_by_char(data=names, current_chars={'.'}, new_char=' ')
        return names, addresses

    def _transform_date(self, date_input: str) -> datetime:
        # log_email_parser.info("Func: _transform_date")
        date_obj = self.dt.parse_email_date(date_input=date_input)
        date_obj = self.dt.change_time_shift(date_input=date_obj)
        return date_obj

    def split_name_address(self, fieldvalue: str) -> list:
        """
        Some names contain one or more commas, which should not be mistaken for a splitting character.
        Avoid cutting names with commas.

        Sometimes a name is the e-mail address, so the person field will contain the address twice,
        and therefore twice '@'.
        """
        # log_email_parser.info("Func: split_name_address")
        if fieldvalue is None:
            return None
        if not isinstance(fieldvalue, str):
            raise TypeError("A string is expected for the 'fieldvalue' argument to the 'split_name_address' method.")
        split_field = []
        field = ''
        for char in fieldvalue:
            field += char
            if char == ',' and 2 >= field.count('@') >= 1:
                field = self.sc.to_lower_and_strip(data=field)
                split_field.append(field[:-1])
                field = ''
        if split_field == []:
            split_field.append(fieldvalue)
        names_address = []
        for field in split_field:
            last_space_index = field.rfind(' ')

            if last_space_index == -1:
                address = self.sc.remove_chars(field)
                names_address.append(('', address))
            else:
                name = field[:last_space_index]
                address = field[last_space_index + 1:]
                name = self.sc.remove_chars(name)
                address = self.sc.remove_chars(address)
                if name == address:
                    names_address.append(('', address))
                else:
                    names_address.append((name, address))
        return names_address

    def separate_names_and_addresses_from_list(self, list_of_name_address_tuple: List[Tuple[str, str]]) -> Tuple[List[str], List[str]]:
        """For e-mail address fields"""
        # log_email_parser.info("Func: separate_names_and_addresses_from_list")
        if not list_of_name_address_tuple:
            return [], []
        names, addresses = zip(*list_of_name_address_tuple)
        return list(names), list(addresses)

