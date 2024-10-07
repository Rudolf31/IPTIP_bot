from babel import Locale
from babel.support import Translations


class TranslationService:
    """
    Service responsible for retreiving translations.
    """
    @classmethod
    def getTranslation(cls, locale: str) -> Translations:
        """
        Returns the translation for the given locale.

        locale - locale string
        """
        locale = Locale.parse(locale)
        return Translations.load('locale', [locale])

    @classmethod
    def getTemplate(cls, translation: Translations, template: str) -> str:
        """
        Returns the template for the given translation.

        translation - Translations object
        template - template id string
        """
        return translation.gettext(template)
