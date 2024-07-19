# Standard Python imports
from email.parser import BytesParser
from email.policy import default
import os
import base64
from bs4 import BeautifulSoup
import quopri
import re
# Project imports
from can_be_deleted import database_utils


#######################################################
# Code below need to be implemented in class EmailProcessing !
#######################################################


def decode_content(part):
    """
    Decode the content of a single part of an email message.

    This function decodes the content of an email part, focusing on text/plain and text/html
    content types. It supports content encoded in various character sets, defaulting to 'utf-8'
    if the charset is not specified. The function returns the decoded text if the content type
    is text/plain or text/html (with 'inline' content disposition or none specified). Otherwise,
    it returns None.

    Args:
        part (email.message.Message): A single part of an email message, which can be the whole
                                      message if it's not multipart.

    Returns:
        str or None: The decoded text content of the part if it is text/plain or text/html. Returns
                     None if the part has a different content type or if it cannot be decoded.

    Note:
        - The function prioritizes decoding of text content and ignores non-text parts or
          attachments.
        - For text/html content, the raw HTML is returned without stripping any tags.
    """
    content_type = part.get_content_type()
    content_disposition = part.get("Content-Disposition", None)

    if content_type == "text/plain" or (
            content_type == "text/html" and (content_disposition is None or "inline" in content_disposition)):
        payload = part.get_payload(decode=True)
        charset = part.get_content_charset() or 'utf-8'  # Use the charset specified in the part, or default to 'utf-8'
        return payload.decode(charset, errors="ignore")
    return None


def get_email_content(msg):
    """
    Extract the text content from an email message.

    This function handles both simple and multipart email messages, extracting
    the first text/plain or text/html content it finds. For multipart messages,
    it recursively searches through all the parts until it finds text content.

    Args:
        msg (email.message.Message): The email message object from which to extract text content.

    Returns:
        str: The decoded text content of the email message if found; otherwise, a message
        indicating that no text content could be found.

    Note:
        - The function prioritizes text/plain content over text/html.
        - In case of text/html content, any HTML tags are not stripped, and the raw HTML is returned.
        - If the email message does not contain any text content, the function returns a default
        message stating "No text content found."
    """
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue  # Skip multipart container, go deeper
            content = decode_content(part)
            if content:
                return content  # Return the first text content found
    else:
        return decode_content(msg)

    return "No text content found."


def extract_attachments(file_path, destination_root, subdir=None):
    """
    Extract attachments from an email file and save them to a specified directory.

    This function parses an email file, extracts all attachments, and saves them
    to a subdirectory within a given root directory. If the subdirectory is not
    specified, it is generated using a unique identifier derived from the email
    content. The function returns the paths to the saved attachments, their names,
    and the subdirectory used.

    :param file_path: Path to the email file from which to extract attachments.
    :param destination_root: Root directory where the attachments will be saved.
    :param subdir: Optional subdirectory within the root for saving attachments.
                   If None, a unique subdirectory is generated.
    :return: A tuple containing a list of file paths to the saved attachments,
             a list of attachment file names, and the name of the subdirectory used.
    """
    file_path_attachments = []
    attachment_names = []

    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=default).parse(f)

    if subdir is None:
        subdir = database_utils.id_generator(msg)
    full_destination_path = os.path.join(destination_root, subdir)
    if not os.path.exists(full_destination_path):
        os.makedirs(full_destination_path)

    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            filename = part.get_filename()
            if filename:
                attachment_file_path = os.path.join(full_destination_path, filename)
                with open(attachment_file_path, 'wb') as fp:
                    fp.write(part.get_payload(decode=True))
                file_path_attachments.append(attachment_file_path)
                attachment_names.append(filename)
    return file_path_attachments, attachment_names, subdir


def extract_email_data(file_path, with_attachments=False):
    """
    Extracts data from an email file and optionally includes attachment information.

    This function parses an email file to extract basic information such as sender,
    recipient, subject, date, and body. If with_attachments is True, it also extracts
    attachments using extract_attachments function and includes their information.
    The function returns a dictionary containing the extracted email data and,
    if applicable, attachment data.

    :param file_path: Path to the email file from which to extract data.
    :param with_attachments: Boolean indicating whether to extract and include
                             attachment information. Defaults to False.
    :return: A dictionary with extracted email data. If with_attachments is True,
             it also includes lists of attachment names and file paths.
    """
    # ToDo: Check that the id is unique when there are multiple attachments
    attachment_names = []
    file_path_attachments = []
    print("Extracting email data from {}".format(file_path))
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=default).parse(f)
    id_ = database_utils.id_generator(msg)

    if with_attachments:
        file_path_attachments, attachment_names, subdir = extract_attachments(file_path=file_path,
                                                                              destination_root=os.getcwd(),
                                                                              subdir=id_)

    # Note: Case-insensitive
    data = {
        'id': id_,
        'file_path': file_path,
        'file_name': os.path.basename(file_path),
        'from': msg['from'],
        'to': msg['to'],
        'cc': msg['cc'] if msg['cc'] else '',
        'bcc': msg['bcc'] if msg['bcc'] else '',
        'subject': msg['subject'],
        'date': msg['date'],
        'body': get_email_content(msg),
        'attachments_names': attachment_names,
        'file_path_attachments': file_path_attachments
    }

    return data


########################################################################################################################
#   Below unused functions !
########################################################################################################################
def decode_base64(data):
    # ToDo: Unused !
    data_cleaned = re.sub(r'[^A-Za-z0-9+/]', '', data.decode('utf-8', errors='ignore'))
    padding_needed = (-len(data_cleaned)) % 4
    data_cleaned += '=' * padding_needed
    try:
        return base64.b64decode(data_cleaned).decode('utf-8', errors='ignore')
    except base64.binascii.Error:
        return "Base64 decoding error"


def decode_quoted_printable(data):
    # ToDo: Unused !
    return quopri.decodestring(data).decode('utf-8', errors='ignore')


def decode_html(data):
    # ToDo: Unused !
    soup = BeautifulSoup(data.decode('utf-8', errors='ignore'), 'html.parser')
    return soup.get_text()
