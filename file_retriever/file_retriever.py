import os


class FileRetriever:
    def __init__(self, path, supported_extensions):
        self.__path = path
        self.__supported_extensions = supported_extensions
        self.__filepath_dict = {}
        self.__time_dict = {}

    def retrieve_files_path(self):
        if os.path.isdir(self.__path):
            for root, dirs, files in os.walk(self.__path):
                for file in files:
                    self.__add_file_to_dict(root, file)
        elif os.path.isfile(self.__path):
            self.__add_file_to_dict(None, os.path.basename(self.__path), single_file=True)
        else:
            raise ValueError(f"{self.__path} n'est ni un dossier ni un fichier valide.")

    def __add_file_to_dict(self, root, file, single_file=False):
        if single_file:
            file_path = self.__path
        else:
            file_path = os.path.join(root, file)

        if file.endswith(tuple(self.__supported_extensions)):
            if file.endswith('.OUTLOOK.COM'):
                self.__filepath_dict.setdefault('.OUTLOOK.COM', []).append(file_path)
            elif file.endswith('.eml'):
                self.__filepath_dict.setdefault('.eml', []).append(file_path)
            elif file.endswith('.mbox'):
                self.__filepath_dict.setdefault('.mbox', []).append(file_path)

    @property
    def filepath_dict(self):
        return self.__filepath_dict
