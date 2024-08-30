import os.path

from .istring_cleaner import IStringCleaner
class StringCleaner(IStringCleaner):
    def __init__(self, exclude_chars=None):
        if exclude_chars is None:
            exclude_chars = ['<', '>', '\\', '/', '"', "'", ':', ';']
        self.exclude_chars = exclude_chars
        self.forbidden_chars_in_file_names = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    def remove_chars(self, data, exclude_chars=None):
        if exclude_chars is None:
            exclude_chars = self.exclude_chars
        if data is None:
            return None
        elif isinstance(data, list):
            return [self.remove_chars(element) for element in data]
        elif isinstance(data, set):
            return {self.remove_chars(element) for element in data}
        elif isinstance(data, tuple):
            return tuple(self.remove_chars(element) for element in data)
        elif isinstance(data, str):
            return ''.join([char for char in data if char not in exclude_chars])
        else:
            raise TypeError(f"[remove_chars] Unsupported type: {type(data)}")

    def contains_repeated_char(self, data, char: str):
        if isinstance(data, str):
            return data.count(char) > 1
        elif isinstance(data, list):
            return [self.contains_repeated_char(item, char) for item in data]
        elif isinstance(data, tuple):
            return tuple(self.contains_repeated_char(item, char) for item in data)
        elif isinstance(data, set):
            return {self.contains_repeated_char(item, char) for item in data}
        else:
            raise TypeError("[contains_repeated_char] Unsupported data type. Please provide a string, list, set, or tuple.")

    def to_lower_and_strip(self, data):
        if isinstance(data, str):
            return data.lower().strip()
        elif isinstance(data, list):
            return [self.to_lower_and_strip(item) for item in data]
        elif isinstance(data, set):
            return {self.to_lower_and_strip(item) for item in data}
        elif isinstance(data, tuple):
            return tuple(self.to_lower_and_strip(item) for item in data)
        elif isinstance(data, dict):
            return {key: self.to_lower_and_strip(value) for key, value in data.items()}
        else:
            raise TypeError(f"[to_lower_and_strip] Unsupported type: {type(data)}")

    def replace_chars_by_char(self, data, current_chars, new_char: str):
        if data is None:
            return None
        elif isinstance(data, list):
            return [self.replace_chars_by_char(element, current_chars, new_char) for element in data]
        elif isinstance(data, set):
            return {self.replace_chars_by_char(element, current_chars, new_char) for element in data}
        elif isinstance(data, tuple):
            return tuple(self.replace_chars_by_char(element, current_chars, new_char) for element in data)
        elif isinstance(data, str):
            for char in current_chars:
                data = data.replace(char, new_char)
            return data
        else:
            raise TypeError(f"[replace_chars_by_char] Unsupported type: {type(data)}")

    def rename_file(self, filename: str, new_name: str) -> str:
        """
        Renames the file by replacing the filename while keeping the extension intact.

        :param filename: Original filename with extension.
        :param new_name: New name to replace the original filename (without extension).
        :return: New filename with the original extension.
        """
        if '.' in filename:
            name, extension = filename.rsplit('.', 1)
            cleaned_new_name = self.remove_chars(data=new_name, exclude_chars=self.forbidden_chars_in_file_names)
            new_filename = f"{cleaned_new_name}.{extension}"
        else:
            new_filename = self.remove_chars(data=new_name, exclude_chars=self.forbidden_chars_in_file_names)
        return new_filename

    def get_filename_without_extension(self, filename: str) -> str:
        """
        Returns the filename without its extension.

        :param filename: The full filename with extension.
        :return: Filename without the extension.
        """
        dot_index = filename.rfind('.')
        if dot_index == -1:
            return filename
        return filename[:dot_index]

    def get_filename_from_path(self, path: str, remove_extension_file: bool = False) -> str:
        """
        Returns the filename from a full file path. Optionally removes the file extension.

        :param path: The full file path.
        :param remove_extension_file: If True, the extension will be removed from the filename.
        :return: Filename, with or without extension based on the argument.
        """
        filename = os.path.basename(path)
        if remove_extension_file:
            filename = self.get_filename_without_extension(filename=filename)
        return filename

    def get_dirname_from_path(self, path: str) -> str:
        if os.path.isdir(path):
            return os.path.basename(os.path.normpath(path))
        return None

    def is_file(self, path: str) -> bool:
        """
        Returns True if the path is a file, False otherwise.

        :param path: The full path to check.
        :return: Boolean indicating whether the path is a file.
        """
        return os.path.isfile(path)

    def is_dir(self, path: str) -> bool:
        """
        Returns True if the path is a directory, False otherwise.

        :param path: The full path to check.
        :return: Boolean indicating whether the path is a directory.
        """
        return os.path.isdir(path)

    def create_directory(self, dir_path: str):
        """
        Creates a directory if it does not already exist.

        :param dir_path: The path of the directory to create.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Directory '{dir_path}' created.")
        else:
            print(f"Directory '{dir_path}' already exists.")

    def file_exists(self, path: str) -> bool:
        """
        Checks if the file exists at the specified path.

        :param path: The full path to check.
        :return: True if the file exists, False otherwise.
        """
        return os.path.isfile(path)
