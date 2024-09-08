# file_detector.py
# Interfaces
from aggregator.ifile_detector import IFileDetector
# Constants
from config.file_constants import FileConstants


class FileDetector(IFileDetector):
    def __init__(self, file_path, perform_content_check=False):
        self.file_path = file_path
        self.perform_content_check = perform_content_check

    def is_email(self) -> bool:
        return self.file_path.lower().endswith(FileConstants.EMAIL_EXTENSIONS)

    def is_mbox(self) -> bool:
        if self.file_path.endswith(FileConstants.MBOX_EXTENSION):
            return True

        # Additional check by reading the content, if enabled
        if self.perform_content_check:
            try:
                with open(self.file_path, 'r', errors='ignore') as f:
                    for line in f:
                        if line.startswith(FileConstants.MBOX_START_LINE):
                            return True
            except:
                pass
        return False

    def detect_type(self) -> str:
        if self.is_email():
            return FileConstants.EMAIL_TYPE
        elif self.is_mbox():
            return FileConstants.MBOX_TYPE
        else:
            return FileConstants.UNKNOWN_TYPE
