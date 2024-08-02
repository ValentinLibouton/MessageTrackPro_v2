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

    def split_name_address_from_str(self, fieldvalue: str) -> tuple:
        if fieldvalue is None:
            return None, None
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

    def split_names_addresses_from_str(self, fieldvalue: str) -> list:
        if fieldvalue is None:
            return None
        split_filed = fieldvalue.split(',')
        extracted_list = []
        for field in split_filed:
            name, email = self.split_name_address_from_str(field)
            extracted_list.append((name, email))
        return extracted_list

    def split_names_addresses_from_list(self, list_of_name_address_tuple: list) -> tuple:
        if not list_of_name_address_tuple:
            return [], []
        names, addresses = zip(*list_of_name_address_tuple)
        return list(names), list(addresses)

    def contains_repeated_char(self, string: str, char: str) -> bool:
        return string.count(char) > 1