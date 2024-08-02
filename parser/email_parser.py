from email import policy
from email.parser import BytesParser
import mailbox
from .iemail_parser import IEmailParser
from utils.string_cleaner import StringCleaner
from utils.date_transformer import DateTransformer
from hasher.hasher import Hasher

class EmailParser(IEmailParser):
    def __init__(self, hasher: Hasher, string_cleaner=None, date_transformer=None):
        self.string_cleaner = string_cleaner if string_cleaner else StringCleaner()
        self.date_transformer = date_transformer if date_transformer else DateTransformer()
        self.hasher = hasher
    def parse_email(self, email_content):
        """
        Analyse le contenu d'un email et retourne un dictionnaire avec les données pertinentes.

        Paramètres:
        email_content (bytes): Le contenu de l'email en bytes.

        Retourne:
        dict: Un dictionnaire contenant les données de l'email.
        """
        msg = BytesParser(policy=policy.default).parsebytes(email_content)
        email_id = self.hasher.hash_string(data=msg)
        body, attachments = self.extract_body_and_attachments(msg=msg)
        date = self.transform_date(msg['date'])
        to_names, to_addresses = self.split_names_addresses(fieldvalue=msg['to'])
        return {
            'email_id': email_id,
            'from': self.name_address(fieldvalue=msg['from']),
            'subject': msg['subject'],
            'date_str': date.strftime('%Y-%m-%d %H:%M:%S'),
            'date_obj': date,
            'date_iso': date.isoformat(),
            'timestamp': date.timestamp(),
            'to': self.names_addresses(fieldvalue=msg['to']),
            'to_names': to_names,
            'to_addresses': to_addresses,
            'cc': self.names_addresses(fieldvalue=msg['cc']),
            'bcc': self.names_addresses(fieldvalue=msg['bcc']),
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
        mbox = mailbox.mbox(file_path)
        emails = []
        for message in mbox:
            email = self.parse_email(message.as_bytes())
            emails.append(email)
        return emails

    def extract_body_and_attachments(self, msg):
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
                # This is an attachment
                filename = part.get_filename()
                content = part.get_payload(decode=True)
                attachment_id = self.hasher.hash_string(data=content)
                if content is not None:
                    attachments.append({
                        'attachment_id': attachment_id,
                        'filename': filename,
                        'content': content
                    })
        return body, attachments

    def name_address(self, fieldvalue: str):
        return self.string_cleaner.split_name_address_from_str(fieldvalue)

    def names_addresses(self, fieldvalue: str):
        return self.string_cleaner.split_names_addresses_from_str(fieldvalue)

    def split_names_addresses(self, fieldvalue: str):
        list_of_tuple = self.string_cleaner.split_names_addresses_from_str(fieldvalue)
        return self.string_cleaner.split_names_addresses_from_list(list_of_tuple)

    def transform_date(self, date_input):
        transformer = self.date_transformer
        date_obj = transformer._parse_email_date(date_input=date_input)
        date_obj = transformer.change_time_shift(date_input=date_obj)
        return date_obj


