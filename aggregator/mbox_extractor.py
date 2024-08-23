import os
import tempfile
import mailbox
from tqdm import tqdm
import sys
import email
from email.parser import BytesParser
from email.policy import default
from typing import Callable
from utils.log import log_mbox_extractor
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed


class MboxExtractor:
    def __init__(self, mbox_file_path: str, temp_dir=None):
        """
        Initialise le streamer avec le chemin du fichier mbox.

        :param mbox_file_path: Chemin vers le fichier mbox à traiter.
        :param temp_dir: Chemin vers le dossier temporaire pour sauvegarder les emails (optionnel).
        """
        log_mbox_extractor.info("Initialize MboxExtractor")
        self.mbox_file_path = mbox_file_path
        if not os.path.isfile(self.mbox_file_path):
            raise FileNotFoundError(f"Mbox file not found: {self.mbox_file_path}")
        self.temp_dir = temp_dir or tempfile.gettempdir()

    def email_generator(self):
        """
        Générateur qui lit le fichier mbox ligne par ligne et yield chaque email complet.

        :yield: Email complet sous forme de bytes.
        """
        log_mbox_extractor.info("email generation")
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

    def extract_emails(self, show_progress: bool = True, num_workers: int = 4):
        """
        Extrait les emails du fichier mbox et les sauvegarde en fichiers temporaires en utilisant ProcessPoolExecutor.

        :param show_progress: Affiche une barre de progression si True.
        :param num_workers: Nombre de processus à utiliser pour le traitement.
        """
        total_emails = self._count_emails()
        generator = self.email_generator()

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            paths = []
            for i, raw_email in enumerate(generator):
                temp_eml_path = os.path.join(self.temp_dir, f'email_{i}.eml')
                paths.append(temp_eml_path)
                future = executor.submit(self._save_email_to_file, raw_email, temp_eml_path)
                futures.append(future)
                log_mbox_extractor.debug(f"Submitted task for email {i + 1}/{total_emails}")

            for i, future in enumerate(as_completed(futures)):
                future.result()  # Raise exception if occurred
                log_mbox_extractor.info(f"Extracted email {i + 1}/{total_emails}")
        return paths

    @staticmethod
    def _save_email_to_file(raw_email, file_path):
        """
        Sauvegarde un email dans un fichier.

        :param raw_email: Email brut sous forme de bytes.
        :param file_path: Chemin du fichier où sauvegarder l'email.
        """
        with open(file_path, 'wb') as f:
            f.write(raw_email)

    def _count_emails(self) -> int:
        """
        Compte le nombre total d'emails dans le fichier mbox pour la barre de progression.

        :return: Nombre total d'emails.
        """
        log_mbox_extractor.info("Count emails in mbox file")
        count = 0
        with open(self.mbox_file_path, 'rb') as f:
            for line in f:
                if line.startswith(b'From '):
                    count += 1
        return count
