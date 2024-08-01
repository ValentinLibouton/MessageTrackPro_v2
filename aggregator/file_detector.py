import os
import sys

from aggregator.ifile_detector import IFileDetector


class FileDetector(IFileDetector):
    EMAIL_EXTENSIONS = ('.eml', '.outlook.com', '.msg', '.pst', '.ost', '.oft', '.olm')

    def __init__(self, file_path):
        self.file_path = file_path

    def is_email(self) -> bool:
        return self.file_path.lower().endswith(self.EMAIL_EXTENSIONS)

    def is_mbox(self) -> bool:
        if self.file_path.endswith('.mbox'):
            return True

        # Vérification supplémentaire en lisant le contenu
        try:
            with open(self.file_path, 'r', errors='ignore') as f:
                for line in f:
                    if line.startswith('From '):
                        return True
        except:
            pass

        return False

    def detect(self) -> str:
        if self.is_email():
            return 'email'
        elif self.is_mbox():
            return 'mbox'
        else:
            return 'unknown'
