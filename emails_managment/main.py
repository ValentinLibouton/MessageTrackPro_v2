from email.parser import BytesParser
from email.policy import default
import os

def extract_attachments(file_path, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=default).parse(f)

    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            filename = part.get_filename()
            if filename:
                file_path = os.path.join(save_dir, filename)
                with open(file_path, 'wb') as fp:
                    fp.write(part.get_payload(decode=True))
                #print(f"Attachment '{filename}' saved in '{save_dir}'.")
def extract_email_data(file_path, with_attachments=False):
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=default).parse(f)

    attachment_names = []
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            attachment_names.append(part.get_filename())

    # Note: Case-insensitive
    email_data = {
        'file_name': os.path.basename(file_path),
        'from': msg['from'],
        'to': msg['to'],
        'cc': msg['cc'] if msg['cc'] else '',
        'bcc': msg['bcc'] if msg['bcc'] else '',
        'subject': msg['subject'],
        'date': msg['date'],
        'body': msg.get_body(preferencelist=('plain')).get_content(),
        'attachments_names': attachment_names,
    }
    if with_attachments:
        extract_attachments(file_path=file_path, save_dir=os.getcwd())
    return email_data

if __name__ == '__main__':
    email_data = extract_email_data(file_path="", with_attachments=True)
    #print(email_data['from'])
    #print(email_data['to'])
    #print(email_data['subject'])
    #print(email_data['date'])
    #print(email_data['body'])
    print(email_data['cc'])
    print(email_data['bcc'])
    print(email_data['attachments_names'])