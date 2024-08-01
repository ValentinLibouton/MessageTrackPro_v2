from email import policy
from email.parser import BytesParser
import mailbox
from .iemail_parser import IEmailParser
from utils.string_cleaner import StringCleaner
from utils.date_transformer import DateTransformer


class EmailParser(IEmailParser):
    def __init__(self, string_cleaner=None, date_transformer=None):
        self.string_cleaner = string_cleaner if string_cleaner else StringCleaner()
        self.date_transformer = date_transformer if date_transformer else DateTransformer()
    def parse_email(self, email_content):
        """
        Analyse le contenu d'un email et retourne un dictionnaire avec les données pertinentes.

        Paramètres:
        email_content (bytes): Le contenu de l'email en bytes.

        Retourne:
        dict: Un dictionnaire contenant les données de l'email.
        """
        msg = BytesParser(policy=policy.default).parsebytes(email_content)
        body, attachments = self.extract_body_and_attachments(msg=msg)
        date = self.transform_date(msg['date'])
        return {
            'from': self.split_name_address(fieldvalue=msg['from']),
            'subject': msg['subject'],
            'date': date,
            'to': self.split_names_addresses(fieldvalue=msg['to']),
            'cc': self.split_names_addresses(fieldvalue=msg['cc']),
            'bcc': self.split_names_addresses(fieldvalue=msg['bcc']),
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
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(part.get_content_charset())
                elif part.get_content_type() == "text/html" and body is None:
                    body = part.get_payload(decode=True).decode(part.get_content_charset())

            elif "attachment" in content_disposition:
                # This is an attachment
                filename = part.get_filename()
                content = part.get_payload(decode=True)
                if content is not None:
                    attachments.append({
                        'filename': filename,
                        'content': content
                    })
        return body, attachments

    def split_name_address(self, fieldvalue: str):
        return self.string_cleaner.split_name_address(fieldvalue)

    def split_names_addresses(self, fieldvalue: str):
        return self.string_cleaner.split_names_addresses(fieldvalue)

    def transform_date(self, date_input):
        transformer = self.date_transformer
        date_obj = transformer.transform_email_date(date_input=date_input)
        date_obj = transformer.change_time_shift(date_input=date_obj)
        return date_obj


