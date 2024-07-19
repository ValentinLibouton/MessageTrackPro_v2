import hashlib


def id_generator(data) -> str:
    """
    Generate a unique identifier using SHA-256 hashing algorithm.

    This function takes any data input, converts it into a string representation,
    encodes it into UTF-8, and then applies SHA-256 hashing to generate a unique
    identifier. The resulting hash is returned as a hexadecimal string.

    :param data: The input data from which to generate the unique identifier. This can be of any type that can be
    converted to a string.
    :return: A hexadecimal string representing the SHA-256 hash of the input data.
    """
    return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

def id_generator_v2(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            sha256.update(block)
    return sha256.hexdigest()