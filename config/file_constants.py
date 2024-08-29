# file_constants.py
class FileConstants:
    # Supported extensions for different types of email files
    SUPPORTED_EMAIL_EXTENSIONS = ['.outlook.com', '.eml', '.mbox', '.msg', '.pst', '.ost', '.oft', '.olm']
    EMAIL_EXTENSIONS = ('.eml', '.outlook.com', '.msg', '.pst', '.ost', '.oft', '.olm')

    # Common patterns used in file detection
    MBOX_EXTENSION = '.mbox'
    MBOX_START_LINE = 'From '

    # File type identifiers
    EMAIL_TYPE = 'email'
    MBOX_TYPE = 'mbox'
    UNKNOWN_TYPE = 'unknown'

    # Dictionary keys for file categorization
    EMAILS_KEY = 'emails'
    MBOX_KEY = 'mboxes'
    UNKNOWN_KEY = 'unknowns'

    TEMP_EML_STORAGE_DIR = '/tmp'

