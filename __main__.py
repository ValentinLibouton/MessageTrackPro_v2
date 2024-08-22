from hasher.hasher import Hasher
from aggregator.email_aggregator import EmailAggregator
from aggregator.file_retriever import FileRetriever
from aggregator.file_detector import FileDetector
from parser.email_parser import EmailParser
from database.email_database import EmailDatabase


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
    #print(path)
    hasher = Hasher()
    supported_extensions = ['.outlook.com', '.eml', '.mbox', '.msg', '.pst', '.ost', '.oft', '.olm']
    file_retriever = FileRetriever(path=path, supported_extensions=supported_extensions,
                                   file_detector_class=FileDetector)
    email_parser = EmailParser(hasher=hasher)
    # file_retriever.retrieve_files_path()
    # print(file_retriever.filepath_dict)
    email_database = EmailDatabase()
    aggregator = EmailAggregator(file_retriever=file_retriever, email_parser=email_parser,
                                 email_database=email_database)

def retrieve():
    from database.database_retriever import DatabaseRetriever

    # db_retriever = DatabaseRetriever(words=['libouton.valentin@protonmail.ch'],
    #                                  words_localization=['everywhere'],  # 'address'],
    #                                  word_operator="OR",
    #                                  start_date="2018-10-17 00:00:00")
    db_retriever = DatabaseRetriever(addresses=['libouton.valentin@protonmail.ch'],
                                     start_date="2018-10-17 00:00:00")

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




if __name__ == '__main__':
    create_and_fill_database()
    #retrieve()
