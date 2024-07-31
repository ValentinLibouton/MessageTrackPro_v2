import hashlib

def clean_string(s):
    if s is None:
        return None
    exclude_char = ['<', '>', '\\', '/', '"', "'"]
    return ''.join([char for char in s if char not in exclude_char])


def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):  # 4 KB chunks
            sha256.update(block)
    return sha256.hexdigest()


def hash_message(data):
    if isinstance(data, bytes):
        msg_bytes = data
    else:
        msg_bytes = data.as_bytes()
    sha256 = hashlib.sha256()
    chunk_size = 8192  # 8 KB chunks
    for i in range(0, len(msg_bytes), chunk_size):
        sha256.update(msg_bytes[i:i + chunk_size])
    return sha256.hexdigest()


def has_multiple_at_signs(input_string):
    """
    Check if the input string contains more than one '@' character.

    Parameters:
    input_string (str): The string to be checked.

    Returns:
    bool: True if the string contains more than one '@' character, False otherwise.

    Example:
    >>> has_multiple_at_signs("test@example.com")
    False
    >>> has_multiple_at_signs("test@@example.com")
    True
    """
    return input_string.count('@') > 1