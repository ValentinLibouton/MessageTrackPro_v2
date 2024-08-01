from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import pytz
from .idate_transformer import IDateTransformer


class DateTransformer(IDateTransformer):
    def __init__(self, date_format='%Y-%m-%d %H:%M:%S', timezone_name='Europe/Brussels'):
        self.date_format = date_format
        self.timezone_name = timezone_name

    def transform_email_date(self, date_input) -> str:
        """
        Transforme l'élément date provenant d'un email en une chaîne formatée.

        Paramètres:
        date_input: L'élément date à transformer. Peut être de type datetime, str, etc.

        Retourne:
        str: La date formatée.
        """
        date_obj = self._parse_email_date(date_input)
        if date_obj is None:
            raise ValueError(f"Invalid email date input: {date_input}")
        return date_obj.strftime(self.date_format)

    def transform_generic_date(self, date_input) -> str:
        """
        Transforme l'élément date générique en une chaîne formatée.

        Paramètres:
        date_input: L'élément date à transformer. Peut être de type datetime, str, etc.

        Retourne:
        str: La date formatée.
        """
        date_obj = self._parse_generic_date(date_input)
        if date_obj is None:
            raise ValueError(f"Invalid generic date input: {date_input}")
        return date_obj.strftime(self.date_format)

    def is_valid_date(self, date_input) -> bool:
        """
        Vérifie si l'élément donné est une date valide.

        Paramètres:
        date_input: L'élément date à vérifier. Peut être de type datetime, str, etc.

        Retourne:
        bool: True si l'élément est une date valide, False sinon.
        """
        return self._parse_email_date(date_input) is not None or self._parse_generic_date(date_input) is not None

    def _parse_email_date(self, date_input):
        """
        Analyse l'élément date provenant d'un email pour le transformer en objet datetime.

        Paramètres:
        date_input: L'élément date à analyser.

        Retourne:
        datetime: L'objet datetime si l'analyse réussit, sinon None.
        """
        if isinstance(date_input, datetime):
            return date_input
        elif isinstance(date_input, str):
            try:
                return parsedate_to_datetime(date_input)
            except (TypeError, ValueError):
                pass
        return None

    def _parse_generic_date(self, date_input):
        """
        Analyse l'élément date générique pour le transformer en objet datetime.

        Paramètres:
        date_input: L'élément date à analyser.

        Retourne:
        datetime: L'objet datetime si l'analyse réussit, sinon None.
        """
        if isinstance(date_input, datetime):
            return date_input
        elif isinstance(date_input, str):
            for fmt in [
                '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m-%d-%Y %H:%M:%S',
                '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M', '%m-%d-%Y %H:%M',
                '%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y'
            ]:
                try:
                    return datetime.strptime(date_input, fmt)
                except ValueError:
                    continue
        return None

    def is_daylight_saving(self, date_input) -> bool:
        tz = pytz.timezone(self.timezone_name)
        try:
            localized_date = tz.localize(date_input, is_dst=None)
        except pytz.AmbiguousTimeError:
            localized_date = tz.localize(date_input, is_dst=False)
        is_dst = localized_date.dst() != timedelta(0)
        return is_dst


    def change_time_shift(self, date_input):
        if self.is_daylight_saving(date_input):
            season_offset = 2 * 3600
        else:
            season_offset = 1 * 3600

        time_shift_in_seconds = {
            '+1200': -12 * 3600,
            '+1100': -11 * 3600,
            '+1000': -10 * 3600,
            '+0930': -9.5 * 3600,  # Australia
            '+0900': -9 * 3600,
            '+0845': 8.75 * 3600,  # Australia
            '+0800': -8 * 3600,
            '+0700': -7 * 3600,
            '+0600': -6 * 3600,
            '+0530': -5.5 * 3600,  # India
            '+0500': -5 * 3600,
            '+0400': -4 * 3600,
            '+0300': -3 * 3600,
            '+0200': -2 * 3600,
            '+0100': -1 * 3600,
            '+0000': 0,
            '-0000': 0,
            '-0100': 1 * 3600,
            '-0200': 2 * 3600,
            '-0300': 3 * 3600,
            '-0400': 4 * 3600,
            '-0500': 5 * 3600,
            '-0600': 6 * 3600,
            '-0700': 7 * 3600,
            '-0800': 8 * 3600,
            '-0900': 9 * 3600,
            '-1000': 10 * 3600,
            '-1100': 11 * 3600,
            '-1200': 12 * 3600,
        }
        for substring, offset in time_shift_in_seconds.items():
            if substring in date_input:
                date_obj = date_obj + timedelta(seconds=offset + season_offset)
        target_timezone = pytz.timezone(self.timezone_name)
        date_obj = date_obj.replace(tzinfo=pytz.utc)
        date_obj = date_obj.astimezone(target_timezone)
        return date_obj