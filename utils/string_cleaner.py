from .istring_cleaner import IStringCleaner
class StringCleaner(IStringCleaner):
    def __init__(self, exclude_chars=None):
        if exclude_chars is None:
            exclude_chars = ['<', '>', '\\', '/', '"', "'", ':', ';']
        self.exclude_chars = exclude_chars

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
