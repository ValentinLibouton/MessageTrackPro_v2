from abc import ABC, abstractmethod


class IEmailParser(ABC):
    @abstractmethod
    def parse_email(self, email_content):
        """
        Analyse le contenu d'un email et retourne un dictionnaire avec les données pertinentes.

        Paramètres:
        email_content (bytes): Le contenu de l'email en bytes.

        Retourne:
        dict: Un dictionnaire contenant les données de l'email.
        """
        pass

    @abstractmethod
    def parse_mbox(self, file_path):
        """
        Analyse le contenu d'un fichier mbox et retourne une liste de dictionnaires avec les données des emails.

        Paramètres:
        file_path (str): Le chemin du fichier mbox.

        Retourne:
        list: Une liste de dictionnaires contenant les données des emails.
        """
        pass
