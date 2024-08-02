from hasher.hasher import Hasher
from aggregator.email_aggregator import EmailAggregator
from aggregator.file_retriever import FileRetriever
from aggregator.file_detector import FileDetector
from parser.email_parser import EmailParser

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

if __name__ == '__main__':
    path = paths_to_dict()['emails_eml']
    #path = paths_to_dict()['all_emails']
    print(path)
    hasher = Hasher()
    supported_extensions = ['.outlook.com', '.eml', '.mbox', '.msg', '.pst', '.ost', '.oft', '.olm']
    file_retriever = FileRetriever(path=path, supported_extensions=supported_extensions,
                                   file_detector_class=FileDetector)
    email_parser = EmailParser(hasher=hasher)
    #file_retriever.retrieve_files_path()
    #print(file_retriever.filepath_dict)

    aggregator = EmailAggregator(file_retriever=file_retriever, email_parser=email_parser)
    print(aggregator.aggregated_data_dict['date_str'])
