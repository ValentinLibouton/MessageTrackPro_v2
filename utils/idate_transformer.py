from abc import ABC, abstractmethod

class IDateTransformer(ABC):
    @abstractmethod
    def transform_email_date(self, date_input) -> str:
        """
        Transforme l'élément date provenant d'un email en une chaîne formatée.

        Paramètres:
        date_input: L'élément date à transformer. Peut être de type datetime, str, etc.

        Retourne:
        str: La date formatée.
        """
        pass

    @abstractmethod
    def transform_generic_date(self, date_input) -> str:
        """
        Transforme l'élément date générique en une chaîne formatée.

        Paramètres:
        date_input: L'élément date à transformer. Peut être de type datetime, str, etc.

        Retourne:
        str: La date formatée.
        """
        pass

    @abstractmethod
    def is_valid_date(self, date_input) -> bool:
        """
        Vérifie si l'élément donné est une date valide.

        Paramètres:
        date_input: L'élément date à vérifier. Peut être de type datetime, str, etc.

        Retourne:
        bool: True si l'élément est une date valide, False sinon.
        """
        pass
