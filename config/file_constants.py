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

    # Encoding types for text extraction
    SUPPORTED_ENCODINGS = [
        "utf-8",  # Most common encoding for modern text files
        "latin-1",  # Common in Western Europe and the Americas
        "ascii",  # Basic English encoding
        "windows-1252",  # Common in Western European languages on Windows
        "iso-8859-1",  # Latin alphabet part 1
        "iso-8859-15",  # Similar to iso-8859-1 with some additional characters
        "shift_jis",  # Common in Japanese
        "euc-jp",  # Japanese encoding
        "big5",  # Traditional Chinese encoding
        "gb2312",  # Simplified Chinese encoding
        "gbk",  # Extended Chinese encoding
        "utf-16",  # Unicode Transformation Format
        "utf-32",  # Unicode Transformation Format (32-bit)
        "cp850",  # DOS-specific encoding, often used for legacy files
        "mac-roman",  # Encoding used on older Macintosh computers
    ]
