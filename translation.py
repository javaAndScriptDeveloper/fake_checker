from deep_translator import GoogleTranslator


class Translator:

    def __init__(self):
        self.supported_translations_list = [
            {
                "label": "English",
                "value": "english"
            },
            {
                "label": "Ukrainian",
                "value": "ukrainian"
            }
        ]

    def translate_to_english(self, text, source_language):
        try:
            translation = GoogleTranslator(source=source_language, target='english').translate(text)
            return translation
        except Exception as e:
            return f"Translation Error: {e}"
