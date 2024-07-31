import hashlib
import os
from .ihashable import IHasher


class Hasher(IHasher):
    def __init__(self, algorithm='sha256'):
        self.algorithm = algorithm

    def hash_string(self, data:str) -> str:
        if isinstance(data, bytes):
            msg_bytes = data
        else:
            msg_bytes = data.encode('utf-8')
        hasher = hashlib.new(self.algorithm)
        chunk_size = 8192  # 8 KB chunks
        for i in range(0, len(msg_bytes), chunk_size):
            hasher.update(msg_bytes[i:i + chunk_size])
        return hasher.hexdigest()

    def hash_file(self, file_path: str) -> str:
        hasher = hashlib.new(self.algorithm)
        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
