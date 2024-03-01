from database_managment import database_utils
from email.parser import BytesParser
from email.policy import default
import os


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
        'body': msg.get_body(preferencelist=('plain')).get_content(),
        'attachments_names': attachment_names if attachment_names else [],
        'file_path_attachments': file_path_attachments if file_path_attachments else []
    }

    return data
