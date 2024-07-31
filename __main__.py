from hasher.hasher import Hasher
from aggregator.email_aggregator import EmailAggregator
from file_retriever.file_retriever import FileRetriever

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
    hasher = Hasher()
    supported_extensions = ['.OUTLOOK.COM', '.eml', '.mbox']
    file_retriever = FileRetriever(path=path, supported_extensions=supported_extensions)
    aggregator = EmailAggregator(hasher, file_retriever)
