import os
import tempfile
import mailbox
from tqdm import tqdm
import sys
import email
from email.parser import BytesParser
from email.policy import default
from typing import Callable


class MboxEmailStreamer:
    def __init__(self, mbox_file_path: str):
        """
        Initialise le streamer avec le chemin du fichier mbox.

        :param mbox_file_path: Chemin vers le fichier mbox à traiter.
        """
        self.mbox_file_path = mbox_file_path
        if not os.path.isfile(self.mbox_file_path):
            raise FileNotFoundError(f"Mbox file not found: {self.mbox_file_path}")

    def email_generator(self):
        """
        Générateur qui lit le fichier mbox ligne par ligne et yield chaque email complet.
        """
        with open(self.mbox_file_path, 'rb') as f:
            message_lines = []
            for line in f:
                if line.startswith(b'From '):
                    if message_lines:
                        yield b''.join(message_lines)
                        message_lines = []
                message_lines.append(line)
            if message_lines:
                yield b''.join(message_lines)

    def process_emails(self, process_function: Callable[[email.message.EmailMessage], None],
                       show_progress: bool = True):
        """
        Traite chaque email en appelant la fonction de traitement fournie.

        :param process_function: Fonction à appeler pour traiter chaque email. Doit accepter un objet EmailMessage.
        :param show_progress: Affiche une barre de progression si True.
        """
        total_emails = self._count_emails()
        generator = self.email_generator()
        progress_bar = tqdm(total=total_emails, desc="Processing emails", unit="email",
                            file=sys.stdout) if show_progress else None

        for raw_email in generator:
            email_message = self._parse_email(raw_email)
            process_function(email_message)
            if progress_bar:
                progress_bar.update(1)

        if progress_bar:
            progress_bar.close()

    def _parse_email(self, raw_email: bytes) -> email.message.EmailMessage:
        """
        Parse le contenu brut de l'email en un objet EmailMessage.

        :param raw_email: Contenu brut de l'email en bytes.
        :return: Objet EmailMessage parsé.
        """
        parser = BytesParser(policy=default)
        email_message = parser.parsebytes(raw_email)
        return email_message

    def _count_emails(self) -> int:
        """
        Compte le nombre total d'emails dans le fichier mbox pour la barre de progression.

        :return: Nombre total d'emails.
        """
        count = 0
        with open(self.mbox_file_path, 'rb') as f:
            for line in f:
                if line.startswith(b'From '):
                    count += 1
        return count
