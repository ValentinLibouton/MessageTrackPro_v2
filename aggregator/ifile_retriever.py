from abc import ABC, abstractmethod

class IFileRetriever(ABC):
    @abstractmethod
    def retrieve_files_path(self):
        pass

    @abstractmethod
    def filepath_dict(self):
        pass

