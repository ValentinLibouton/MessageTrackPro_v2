from .istring_cleaner import IStringCleaner
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

    def split_name_address(self, fieldvalue: str) -> list:
        if fieldvalue is None:
            return None
        names_address = []
        split_filed = fieldvalue.split(',')
        for field in split_filed:
            trimmed_field = self.to_lower_and_trim(string=field)
            last_space_index = trimmed_field.rfind(' ')

            if last_space_index == -1:
                address = self.remove_chars(trimmed_field)
                names_address.append(('', address))
            else:
                name = trimmed_field[:last_space_index]
                address = trimmed_field[last_space_index+1:]
                name = self.remove_chars(name)
                address = self.remove_chars(address)
                names_address.append((name, address))
        return names_address


    def separate_names_and_addresses_from_list(self, list_of_name_address_tuple: list) -> tuple:
        """For e-mail address fields"""
        if not list_of_name_address_tuple:
            return [], []
        names, addresses = zip(*list_of_name_address_tuple)
        return list(names), list(addresses)

    def contains_repeated_char(self, string: str, char: str) -> bool:
        return string.count(char) > 1

    def to_lower_and_trim(self, string: str) -> str:
        return string.lower().strip()

    def replace_chars_by_char(self, fieldvalue, current_chars, new_char: str):
        if fieldvalue is None:
            return None
        elif isinstance(fieldvalue, list):
            return [self.replace_chars_by_char(element, current_chars, new_char) for element in fieldvalue]
        elif isinstance(fieldvalue, set):
            return {self.replace_chars_by_char(element, current_chars, new_char) for element in fieldvalue}
        elif isinstance(fieldvalue, tuple):
            return tuple(self.replace_chars_by_char(element, current_chars, new_char) for element in fieldvalue)
        elif isinstance(fieldvalue, str):
            for char in current_chars:
                fieldvalue = fieldvalue.replace(char, new_char)
            return fieldvalue
        else:
            raise TypeError(f"Unsupported type: {type(fieldvalue)}")
