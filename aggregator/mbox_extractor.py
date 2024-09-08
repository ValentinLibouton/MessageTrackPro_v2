# mbox_extractor.py
# Libraries
import os
import tempfile
from typing import Iterator, List
from concurrent.futures import ProcessPoolExecutor, as_completed
# Interfaces
from aggregator.imbox_extractor import ImboxExtractor
# Constants
from config.system_config import SystemConfig
# Personal libraries
from utils.logging_setup import log_mbox_extractor


class MboxExtractor(ImboxExtractor):
    def __init__(self, mbox_file_path: str, temp_dir=None):
        """
        Initializes streamer with mbox file path.

        :param mbox_file_path: Path to mbox file to be processed.
        :param temp_dir: Path to temporary folder for saving emails (optional).
        """
        log_mbox_extractor.info("Initialize MboxExtractor")
        self.mbox_file_path = mbox_file_path
        if not os.path.isfile(self.mbox_file_path):
            raise FileNotFoundError(f"Mbox file not found: {self.mbox_file_path}")
        self.temp_dir = temp_dir or tempfile.gettempdir()

    def extract_emails(self, show_progress: bool = True, num_workers: int = SystemConfig.MAX_WORKERS) -> List[str]:
        total_emails = self._count_emails(mbox_file_path=self.mbox_file_path)
        generator = self._email_generator(mbox_file_path=self.mbox_file_path)

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            paths = []
            for i, byte_email in enumerate(generator):
                temp_eml_path = os.path.join(self.temp_dir, f'email_{i}.eml')
                paths.append(temp_eml_path)
                future = executor.submit(self._save_email_to_file, byte_email, temp_eml_path)
                futures.append(future)
                log_mbox_extractor.debug(f"Submitted task for email {i + 1}/{total_emails}")

            for i, future in enumerate(as_completed(futures)):
                future.result()  # Raise exception if occurred
                log_mbox_extractor.info(f"Extracted email {i + 1}/{total_emails}")
        return paths

    @staticmethod
    def _count_emails(self, mbox_file_path: str) -> int:
        log_mbox_extractor.info("Count emails in mbox file")
        count = 0
        with open(mbox_file_path, 'rb') as f:
            for line in f:
                if line.startswith(b'From '):
                    count += 1
        return count

    @staticmethod
    def _email_generator(self, mbox_file_path: str) -> Iterator[bytes]:
        log_mbox_extractor.info("email generation")
        with open(mbox_file_path, 'rb') as f:
            message_lines = []
            for line in f:
                if line.startswith(b'From '):
                    if message_lines:
                        yield b''.join(message_lines)
                        message_lines = []
                message_lines.append(line)
            if message_lines:
                yield b''.join(message_lines)

    @staticmethod
    def _save_email_to_file(byte_email: bytes, file_path: str) -> None:
        with open(file_path, 'wb') as f:
            f.write(byte_email)
