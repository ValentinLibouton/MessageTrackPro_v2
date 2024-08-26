from aggregator.email_aggregator import EmailAggregator
from aggregator.file_retriever import FileRetriever
from parser.email_parser import EmailParser
from database.email_database import EmailDatabase
import os
from config.file_constants import FileConstants

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

def create_and_fill_database():
    #path = paths_to_dict()['emails_eml']
    path = paths_to_dict()['all_emails']

    file_retriever = FileRetriever(path=path, supported_extensions=FileConstants.SUPPORTED_EMAIL_EXTENSIONS)
    attachments_path = paths_to_dict()['attachments']
    email_parser = EmailParser(attachments_directory=attachments_path)
    email_database = EmailDatabase()
    mbox_temp_directory = paths_to_dict()['tmp']
    aggregator = EmailAggregator(file_retriever=file_retriever, email_parser=email_parser,
                                 email_database=email_database, mbox_temp_directory=mbox_temp_directory)

def retrieve():
    from database.database_retriever import DatabaseRetriever
    db_retriever = DatabaseRetriever(addresses=['libouton.valentin'])

    # Build the query with joins and where conditions
    db_retriever.join().where()

    # Show the query before executing it
    query = db_retriever.show_query()
    print("SQL Query:")
    print(query)

    # Execute the query and retrieve the IDs
    ids = db_retriever.execute()

    # Print the results
    for i, id in enumerate(ids, start=1):
        print(f"ID{i}:\t{id[0]}")


def list_files(startpath, exclude=None):
    if exclude is None:
        exclude = []

    for root, dirs, files in os.walk(startpath):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude]

        # Print directory
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")

        # Print files
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in exclude:
                print(f"{subindent}{f}")


# Example usage



if __name__ == '__main__':
    create_and_fill_database()
    #retrieve()

    #exclude_list = ['__pycache__', '.git', 'venv', 'attachments', '.gitignore', '.idea']
    #list_files('.', exclude=exclude_list)
