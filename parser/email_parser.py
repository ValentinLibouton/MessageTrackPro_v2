# email_parser.py
# Libraries
import gc
import os
from email import policy
from email.parser import BytesParser
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Union, Any
from abc import abstractmethod
from email.message import Message
# Interfaces
from .iemail_parser import IEmailParser
# Constants
from config.email_parser_constants import EmailParserConstants
from config.email_constants import *
# Personal libraries
from utils.file_content_extractor import FileContentExtractor
from utils.string_cleaner import StringCleaner
from utils.date_transformer import DateTransformer
from utils.logging_setup import log_email_parser_info, log_email_parser_debug, log_email_parser_warning
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
        log_email_parser_info.info("Func: parse_email")
        msg = BytesParser(policy=policy.default).parsebytes(email_content)
        email_id = self.hasher.hash_string(data=msg.as_bytes())
        log_email_parser_debug.debug(f"Func: parse_email for email_id: {email_id}")
        date = self._transform_date(msg['date'])
        log_email_parser_debug.debug(f"Func: parse_email with date: {date}")
        body, attachments = self.extract_body_and_attachments(msg=msg)

        from_name, from_address = self._parse_names_addresses(data=msg['from'])
        to_names, to_addresses = self._parse_names_addresses(data=msg['to'])
        cc_names, cc_addresses = self._parse_names_addresses(data=msg['cc'])
        bcc_names, bcc_addresses = self._parse_names_addresses(data=msg['bcc'])
        log_email_parser_debug.debug(f"from_name: {from_name}")
        log_email_parser_debug.debug(f"to_names: {to_names}")
        log_email_parser_debug.debug(f"cc_names: {cc_names}")
        log_email_parser_debug.debug(f"bcc_names: {bcc_names}")

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
        log_email_parser_info.info("Func: extract_body_and_attachments")
        body = None
        attachments = []
        for part in msg.walk():
            content_disposition = part.get('Content-Disposition')
            if self._is_multipart(part=part):
                continue  # Skip multipart container, go deeper
            elif self._is_body_part(part=part):
                if part.get_content_type() in ["text/plain", "text/html"]:
                    charset = part.get_content_charset()
                    if charset:
                        try:
                            # Attempt to decode with the specified charset
                            body_content = part.get_payload(decode=True).decode(charset)
                        except (LookupError, UnicodeDecodeError):
                            # Fallback to utf-8 if charset is unknown or decoding fails
                            log_email_parser_warning.warning(
                                f"Unknown or invalid charset '{charset}', falling back to 'utf-8'.")
                            body_content = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    else:
                        # No charset specified, default to utf-8
                        body_content = part.get_payload(decode=True).decode('utf-8', errors='replace')

                    if part.get_content_type() == "text/plain" or body is None:
                        body = body_content

            elif "attachment" in content_disposition:
                log_email_parser_info.info("Func: extract_body_and_attachments, attachment found.")
                # This is an attachment
                filename = part.get_filename()
                content = part.get_payload(decode=True)
                if content is not None:
                    attachment_id = self.hasher.hash_string(data=content)
                    log_email_parser_debug.debug(f"Func: extract_body_and_attachments, attachment_id: {attachment_id}")
                    filepath = self._download_attachment(content=content, attachment_id=attachment_id, filename=filename)
                    file_text_extractor = FileContentExtractor(file_path=filepath)
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

    def _is_multipart(self, part) -> bool:
        return part.get_content_maintype() == 'multipart'

    def _is_multipart_mixed(self, part: Message) -> bool:
        """
        Checks if the email part is of type multipart/mixed.

        multipart/mixed is used for emails that contain multiple parts of different types,
        such as text, images, or attachments, all intended to be processed separately.

        :param part: The email part to check.
        :return: True if the part is multipart/mixed, False otherwise.
        """
        return part.get_content_type() == 'multipart/mixed'

    def _is_multipart_alternative(self, part: Message) -> bool:
        """
        Checks if the email part is of type multipart/alternative.

        multipart/alternative is used when the email contains different versions
        of the same content, like plain text and HTML, where the recipient's client
        chooses which one to display.

        :param part: The email part to check.
        :return: True if the part is multipart/alternative, False otherwise.
        """
        return part.get_content_type() == 'multipart/alternative'

    def _is_multipart_related(self, part: Message) -> bool:
        """
        Checks if the email part is of type multipart/related.

        multipart/related is used for emails where different parts are intended to be
        displayed together, such as an HTML email with embedded images.

        :param part: The email part to check.
        :return: True if the part is multipart/related, False otherwise.
        """
        return part.get_content_type() == 'multipart/related'

    def _is_multipart_form_data(self, part: Message) -> bool:
        """
        Checks if the email part is of type multipart/form-data.

        multipart/form-data is typically used for forms that submit file uploads
        and other binary data alongside text fields.

        :param part: The email part to check.
        :return: True if the part is multipart/form-data, False otherwise.
        """
        return part.get_content_type() == 'multipart/form-data'

    def _is_multipart_signed(self, part: Message) -> bool:
        """
        Checks if the email part is of type multipart/signed.

        multipart/signed is used to attach a digital signature to the email, ensuring
        the integrity and authenticity of the message.

        :param part: The email part to check.
        :return: True if the part is multipart/signed, False otherwise.
        """
        return part.get_content_type() == 'multipart/signed'

    def _is_body_part(self, part) -> bool:
        # This is the email body
        content_disposition = part.get('Content-Disposition')
        return content_disposition is None


    def _download_attachment(self, content: Any, attachment_id: str, filename: str) -> None:
        try:
            self.sc.create_directory(dir_path=self.attachments_directory)
            new_filename = self.sc.rename_file(filename=filename, new_name=attachment_id)
            filepath = os.path.join(self.attachments_directory, new_filename)
            if not self.sc.file_exists(filepath):
                log_email_parser_info.info(f"Download attachment {filepath}")
                with open(filepath, 'wb') as f:
                    f.write(content)
            else:
                log_email_parser_debug.debug(f"Attachment {filename} already exists")
            return filepath
        except Exception as e:
            raise Exception(f"{filename}: {e}")

    def _parse_names_addresses(self, data: str) -> Tuple[List[str], List[str]]:
        log_email_parser_debug.debug(f"Func: _parse_names_addresses {data}")
        list_names_and_addresses = self.split_name_address(fieldvalue=data)
        names, addresses = self.separate_names_and_addresses_from_list(list_names_and_addresses)
        names = self.sc.replace_chars_by_char(data=names, current_chars={'.'}, new_char=' ')
        return names, addresses

    def _transform_date(self, date_input: str) -> datetime:
        log_email_parser_debug.debug(f"Func: _transform_date {date_input}")
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
        log_email_parser_debug.debug(f"Func: split_name_address {fieldvalue}")
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
        log_email_parser_debug.debug(f" Func: separate_names_and_addresses_from_list {list_of_name_address_tuple}")
        if not list_of_name_address_tuple:
            return [], []
        names, addresses = zip(*list_of_name_address_tuple)
        return list(names), list(addresses)

