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


def extract_name_and_email(fieldvalues: str):
    trimmed_field = fieldvalues.strip()
    last_space_index = trimmed_field.rfind(' ')

    if last_space_index == -1:
        address = clean_string(trimmed_field)
        return '', address

    name = trimmed_field[:last_space_index]
    address = trimmed_field[last_space_index + 1:]
    name = clean_string(name)
    address = clean_string(address)
    return name, address


def extract_multiple_names_and_emails(fieldvalues):
    splited_filed = fieldvalues.split(',')
    extracted_list = []
    for field in splited_filed:
        name, email = extract_name_and_email(field)
        d = {'name': name, 'email': email}
        extracted_list.append(d)
    return extracted_list


def is_daylight_saving(date, timezone='Europe/Brussels'):
    tz = pytz.timezone(timezone)
    try:
        localized_date = tz.localize(date, is_dst=None)
    except pytz.AmbiguousTimeError:
        localized_date = tz.localize(date, is_dst=False)
    is_dst = localized_date.dst() != timedelta(0)
    return is_dst

def decode_content(part):
    content_type = part.get_content_type()
    content_disposition = part.get("Content-Disposition", None)

    if content_type in ["text/plain", "text/html"] and (
            content_disposition is None or "inline" in content_disposition):
        payload = part.get_payload(decode=True)
        charset = part.get_content_charset() or 'utf-8'  # Use the charset specified in the part, or default to 'utf-8'
        try:
            return payload.decode(charset, errors="replace")
        except LookupError:
            return payload.decode('utf-8', errors="replace")
    return None


def convert_date_to_datetime(date_str, target_tz="Europe/Brussels"):
    parsed_date = email.utils.parsedate(date_str)
    if parsed_date is None:
        return None
    date_obj = datetime(*parsed_date[:6])

    if is_daylight_saving(date=date_obj):  #for Europe/Brussels
        season_offset = 2 * 3600
    else:
        season_offset = 1 * 3600
    time_shift_in_seconds = {
        '+1200': -12 * 3600,
        '+1100': -11 * 3600,
        '+1000': -10 * 3600,
        '+0930': -9.5 * 3600,  # Australia
        '+0900': -9 * 3600,
        '+0845': 8.75 * 3600,  # Australia
        '+0800': -8 * 3600,
        '+0700': -7 * 3600,
        '+0600': -6 * 3600,
        '+0530': -5.5 * 3600,  # India
        '+0500': -5 * 3600,
        '+0400': -4 * 3600,
        '+0300': -3 * 3600,
        '+0200': -2 * 3600,
        '+0100': -1 * 3600,
        '+0000': 0,
        '-0000': 0,
        '-0100': 1 * 3600,
        '-0200': 2 * 3600,
        '-0300': 3 * 3600,
        '-0400': 4 * 3600,
        '-0500': 5 * 3600,
        '-0600': 6 * 3600,
        '-0700': 7 * 3600,
        '-0800': 8 * 3600,
        '-0900': 9 * 3600,
        '-1000': 10 * 3600,
        '-1100': 11 * 3600,
        '-1200': 12 * 3600,

    }
    for substring, offset in time_shift_in_seconds.items():
        if substring in date_str:
            date_obj = date_obj + timedelta(seconds=offset + season_offset)
    target_timezone = pytz.timezone(target_tz)
    date_obj = date_obj.replace(tzinfo=pytz.utc)
    date_obj = date_obj.astimezone(target_timezone)

    return date_obj


def split_names_and_emails(addresses, string_cleaning=True):
    if addresses is None:
        return None, None
    names = []
    emails = []
    for d in addresses:
        name = d.get('name', None)
        email = d.get('email', None)
        """
        if string_cleaning:
            name = clean_string(s=name)
            email = clean_string(s=email)
        """
        names.append(name)
        emails.append(email)
    return names, emails