import os
from aggregator.file_detector import FileDetector
from aggregator.ifile_retriever import IFileRetriever

class FileRetriever(IFileRetriever):
    def __init__(self, path, supported_extensions, file_detector_class=FileDetector):
        self.__path = path
        self.__supported_extensions = supported_extensions
        self.__filepath_dict = {}
        self.file_detector_class = file_detector_class

    def retrieve_files_path(self):
        #print(f"Exploration du chemin : {self.__path}")
        if os.path.isdir(self.__path):
            for root, dirs, files in os.walk(self.__path):
                for file in files:
                    #print(f"Fichier trouvé : {file}")
                    self.__add_file_to_dict(root, file)
        elif os.path.isfile(self.__path):
            #print(f"Fichier unique trouvé : {self.__path}")
            self.__add_file_to_dict(None, os.path.basename(self.__path), single_file=True)
        else:
            raise ValueError(f"{self.__path} n'est ni un dossier ni un fichier valide.")

    def __add_file_to_dict(self, root, file, single_file=False):
        if single_file:
            file_path = self.__path
        else:
            file_path = os.path.join(root, file)

        #print(f"Analyse du fichier : {file_path}")
        detector = self.file_detector_class(file_path)
        file_type = detector.detect()

        if file_type == 'email':
            #print(f"Fichier email détecté : {file_path}")
            self.__filepath_dict.setdefault('emails', []).append(file_path)
        elif file_type == 'mbox':
            #print(f"Fichier mbox détecté : {file_path}")
            self.__filepath_dict.setdefault('mbox', []).append(file_path)
        else:
            #print(f"Fichier inconnu détecté : {file_path}")
            self.__filepath_dict.setdefault('unknown', []).append(file_path)


    @property
    def filepath_dict(self):
        return self.__filepath_dict
