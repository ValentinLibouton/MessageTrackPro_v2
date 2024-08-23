import gc
import os
from email import policy
from email.parser import BytesParser
import mailbox
from .iemail_parser import IEmailParser
from utils.string_cleaner import StringCleaner
from utils.date_transformer import DateTransformer
from hasher.hasher import Hasher
from utils.log import log_email_parser

class EmailParser(IEmailParser):
    def __init__(self, hasher: Hasher, string_cleaner=None, date_transformer=None):
        self.sc = string_cleaner if string_cleaner else StringCleaner()
        self.dt = date_transformer if date_transformer else DateTransformer()
        self.hasher = hasher

    def parse_email(self, email_content):
        """
        Analyse le contenu d'un email et retourne un dictionnaire avec les données pertinentes.

        Paramètres:
        email_content (bytes): Le contenu de l'email en bytes.

        Retourne:
        dict: Un dictionnaire contenant les données de l'email.
        """
        log_email_parser.info("Func: parse_email")
        msg = BytesParser(policy=policy.default).parsebytes(email_content)
        # print(f"msg keys: {msg.keys()}")
        email_id = self.hasher.hash_string(data=msg.as_bytes())
        #print(f"email_id: {email_id}")
        body, attachments = self.extract_body_and_attachments(msg=msg)
        # print(f"Date: {msg['date']}")
        date = self._transform_date(msg['date'])

        from_name, from_address = self._parse_names_addresses(data=msg['from'])
        to_names, to_addresses = self._parse_names_addresses(data=msg['to'])
        cc_names, cc_addresses = self._parse_names_addresses(data=msg['cc'])
        bcc_names, bcc_addresses = self._parse_names_addresses(data=msg['bcc'])


        return {
            'email_id': email_id,
            'from_name': from_name,
            'from_address': from_address,
            'subject': msg['subject'],
            'date_str': date.strftime('%Y-%m-%d %H:%M:%S') if date else None,
            'date_obj': date if date else None,
            'date_iso': date.isoformat() if date else None,
            'timestamp': date.timestamp() if date else None,
            'to_names': to_names,
            'to_addresses': to_addresses,
            'cc_names': cc_names,
            'cc_addresses': cc_addresses,
            'bcc_names': bcc_names,
            'bcc_addresses': bcc_addresses,
            'body': body,
            'attachments': attachments
        }

    def parse_mbox(self, file_path):
        """
        Analyse le contenu d'un fichier mbox et retourne une liste de dictionnaires avec les données des emails.

        Paramètres:
        file_path (str): Le chemin du fichier mbox.

        Retourne:
        list: Une liste de dictionnaires contenant les données des emails.
        """
        log_email_parser.info("Func: parse_mbox")
        mbox = mailbox.mbox(file_path)
        emails = []
        for message in mbox:
            email = self.parse_email(message.as_bytes())
            emails.append(email)
        return emails

    def extract_body_and_attachments(self, msg):
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
                    charset = part.get_content_charset() or 'utf-8'  # Default to 'utf-8' if charset is Non
                    try:
                        body_content = part.get_payload(decode=True).decode(charset)
                    except UnicodeDecodeError:
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
                    self._download_attachment(content=content, attachment_id=attachment_id, filename=filename)
                    # ToDo !!!
                    #extractor = AttachmentTextExtractor(file_content=content)
                    #extracted_text = extractor.extract_text()
                    attachments.append({
                        'attachment_id': attachment_id,
                        'filename': filename,
                        'content': content,
                        'extracted_text': "extracted_text" # Todo !!!!
                    })
                    del content
                    gc.collect()
                else:
                    # Handle the case where content is None
                    print(f"Warning: Attachment {filename} has no content and was skipped.")
        return body, attachments

    def _download_attachment(self, content, attachment_id, filename, save_directory="attachments"):
        log_email_parser.info("Func: _download_attachment")
        try:
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            new_filename = self.sc.rename_file(filename=filename, new_name=attachment_id)
            filepath = os.path.join(save_directory, new_filename)

            with open(filepath, 'wb') as f:
                f.write(content)

            #print(f"Attachment saved to {filepath}")
        except Exception as e:
            raise Exception(f"{filename}: {e}")


    def _parse_names_addresses(self, data):
        #log_email_parser.info("Func: _parse_names_addresses")
        list_names_and_addresses = self.split_name_address(fieldvalue=data)
        names, addresses = self.separate_names_and_addresses_from_list(list_names_and_addresses)
        names = self.sc.replace_chars_by_char(data=names, current_chars={'.'}, new_char=' ')
        return names, addresses


    def _transform_date(self, date_input):
        #log_email_parser.info("Func: _transform_date")
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
        #log_email_parser.info("Func: split_name_address")
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
        # split_field = fieldvalue.split(',')
        for field in split_field:
            # print(f"Address field: {field}")
            last_space_index = field.rfind(' ')

            if last_space_index == -1:
                address = self.sc.remove_chars(field)
                names_address.append(('', address))
            else:
                name = field[:last_space_index]
                address = field[last_space_index+1:]
                name = self.sc.remove_chars(name)
                address = self.sc.remove_chars(address)
                if name == address:
                    names_address.append(('', address))
                else:
                    names_address.append((name, address))
        return names_address


    def separate_names_and_addresses_from_list(self, list_of_name_address_tuple: list) -> tuple:
        """For e-mail address fields"""
        #log_email_parser.info("Func: separate_names_and_addresses_from_list")
        if not list_of_name_address_tuple:
            return [], []
        names, addresses = zip(*list_of_name_address_tuple)
        return list(names), list(addresses)
