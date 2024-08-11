from .icleaner import IStringCleaner
class StringCleaner(IStringCleaner):
    def __init__(self, exclude_chars=None):
        if exclude_chars is None:
            exclude_chars = ['<', '>', '\\', '/', '"', "'"]
        self.exclude_chars = exclude_chars

    def remove_chars(self, fieldvalue, exclude_chars=None):
        if exclude_chars is None:
            exclude_chars = self.exclude_chars
        if fieldvalue is None:
            return None
        elif isinstance(fieldvalue, list):
            return [self.remove_chars(element) for element in fieldvalue]
        elif isinstance(fieldvalue, set):
            return {self.remove_chars(element) for element in fieldvalue}
        elif isinstance(fieldvalue, tuple):
            return tuple(self.remove_chars(element) for element in fieldvalue)
        elif isinstance(fieldvalue, str):
            return ''.join([char for char in fieldvalue if char not in exclude_chars])
        else:
            raise TypeError(f"Unsupported type: {type(fieldvalue)}")

    def split_name_address_from_str(self, fieldvalue: str) -> tuple:
        """For e-mail address fields"""
        if fieldvalue is None:
            return None, None
        trimmed_field = fieldvalue.strip()
        last_space_index = trimmed_field.rfind(' ')

        if last_space_index == -1:
            address = self.remove_chars(trimmed_field)
            return '', address

        name = trimmed_field[:last_space_index]
        address = trimmed_field[last_space_index + 1:]
        name = self.remove_chars(name)
        address = self.remove_chars(address)
        return name, address

    def split_names_addresses_from_str(self, fieldvalue: str) -> list:
        """For e-mail address fields"""
        if fieldvalue is None:
            return None
        split_filed = fieldvalue.split(',')
        extracted_list = []
        for field in split_filed:
            name, email = self.split_name_address_from_str(field)
            extracted_list.append((name, email))
        return extracted_list

    def split_names_addresses_from_list(self, list_of_name_address_tuple: list) -> tuple:
        """For e-mail address fields"""
        if not list_of_name_address_tuple:
            return [], []
        names, addresses = zip(*list_of_name_address_tuple)
        return list(names), list(addresses)

    def contains_repeated_char(self, string: str, char: str) -> bool:
        return string.count(char) > 1

    def to_lower_and_trim(self, string: str) -> str:
        return string.lower().strip()

    def replace_chars_by_char(self, fieldvalue, current_chars: list, new_char: str):
        if fieldvalue is None:
            return None
        elif isinstance(fieldvalue, list):
            return [self.replace_chars_by_char(element, current_chars) for element in fieldvalue]
        elif isinstance(fieldvalue, set):
            return {self.replace_chars_by_char(element, current_chars) for element in fieldvalue}
        elif isinstance(fieldvalue, tuple):
            return tuple(self.replace_char(element, current_chars) for element in fieldvalue)
        elif isinstance(fieldvalue, str):
            for char in current_chars:
                fieldvalue = fieldvalue.replace(char, new_char)
            return fieldvalue
        else:
            raise TypeError(f"Unsupported type: {type(fieldvalue)}")
