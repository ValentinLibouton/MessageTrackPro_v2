from .icleaner import IStringCleaner
class StringCleaner(IStringCleaner):
    def __init__(self, exclude_chars=None):
        if exclude_chars is None:
            exclude_chars = ['<', '>', '\\', '/', '"', "'"]
        self.exclude_chars = exclude_chars

    def clean(self, string: str) -> str:
        if string is None:
            return None
        return ''.join([char for char in string if char not in self.exclude_chars])

    def split_name_address(self, fieldvalue: str) -> tuple:
        trimmed_field = fieldvalue.strip()
        last_space_index = trimmed_field.rfind(' ')

        if last_space_index == -1:
            address = self.clean(trimmed_field)
            return '', address

        name = trimmed_field[:last_space_index]
        address = trimmed_field[last_space_index + 1:]
        name = self.clean(name)
        address = self.clean(address)
        return name, address

    def split_names_addresses(self, fieldvalue: str) -> list:
        split_filed = fieldvalue.split(',')
        extracted_list = []
        for field in split_filed:
            name, email = self.split_name_address(field)
            extracted_list.append((name, email))
        return extracted_list

    def contains_repeated_char(self, string: str, char: str) -> bool:
        return string.count(char) > 1