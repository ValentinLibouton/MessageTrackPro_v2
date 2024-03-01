from database_managment import database_utils
from email.parser import BytesParser
from email.policy import default
import os


def extract_attachments(file_path, destination_root, subdir=None):
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
