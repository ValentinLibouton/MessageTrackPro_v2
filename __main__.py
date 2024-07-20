from emails_managment.email_processing import EmailProcessing
from tabulate import tabulate
path = input("path: ")
ep = EmailProcessing(path=path, with_attachments=True)
df = ep.get_emails()
print(df)