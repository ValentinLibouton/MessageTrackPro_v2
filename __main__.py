from emails_managment.email_processing import EmailProcessing
from database_managment.email_database import *

def paths_to_dict():
    """This is a temporary function for project development..."""
    paths = {}
    with open('paths.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                k, v = line.split(' ',1)
                paths[k] = v.strip()
    return paths



if __name__ == "__main__":
    path = paths_to_dict()['emails_eml']
    ep = EmailProcessing(path=path, with_attachments=True)
    emails = ep.get_emails_list
    process_emails(emails=emails)
    print(ep.log_execution_time)