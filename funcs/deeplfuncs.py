import os
import deepl
import random
import string


def get_columns():
    return deeplWrapper.get_columns()


def get_languages():
    return deeplWrapper.get_languages()

def check_api_key():
    return 'DEEPL_KEY' in os.environ

# Wrap/mock DeepL calls.
class deeplWrapper:

    # Vast majority of English problem text is British, currently.
    # Fixit Clinic is only US English, too few to make a case for 'en-us' just yet.
    # There are a few Danish (DNK) records in the dataset, so will need 'da' before long.
    langdict = {'en': 'en-gb', 'de': 'de', 'nl': 'nl',
                'fr': 'fr', 'it': 'it', 'es': 'es', 'da': 'da'}

    def __init__(self, mock=False):
        if mock:
            self.translator = mockDeepLTranslator()
        else:
            if 'DEEPL_KEY' in os.environ:
                auth_key = os.environ['DEEPL_KEY']
                self.translator = deepl.Translator(auth_key)
            else:
                print('ERROR! DEEPL_KEY NOT FOUND!')
                print('Add your DeepL API key to the .env file.')
                self.translator = False

    def translate_text(self, text, target_lang, source_lang=''):
        return self.translator.translate_text(text, target_lang=target_lang, source_lang=source_lang)

    def api_limit_reached(self):
        usage = self.translator.get_usage()
        if usage.character.valid:
            print(
                f"Character usage: {usage.character.count} of {usage.character.limit}")
        if usage.any_limit_reached:
            print('Translation limit reached.')
            return True
        return False

    def get_languages():
        return list(deeplWrapper.langdict.values())

    def get_columns():
        return list(deeplWrapper.langdict.keys())


# To Do: mock exception
class mockDeepLTranslator:

    def translate_text(self, text, target_lang, source_lang=''):
        self.detected_source_lang = mockDeepLTranslator.mockTranslation(
            len=2, up=True)
        self.text = mockDeepLTranslator.mockTranslation()
        return self

    def get_usage(self):
        return mockDeepLUsage()

    @staticmethod
    def mockTranslation(len=0, lo=False, up=False, ws=False, nums=False, punct=False):
        if len == 0:
            len = random.randint(6, 12)

        if lo:
            chars = string.ascii_lowercase
        elif up:
            chars = string.ascii_uppercase
        else:
            chars = string.ascii_letters

        if ws:
            chars = chars + string.whitespace
        if nums:
            chars = chars + string.punctuation
        if nums:
            chars = chars + string.digits
        return ''.join(random.choice(chars) for i in range(len))


# mock DeepL usage class for testing.
class mockDeepLUsage:
    def __init__(self):
        self.character = mockDeepLUsageChar()
        self.any_limit_reached = False


# mock DeepL usage class for testing.
class mockDeepLUsageChar:
    def __init__(self):
        self.valid = True
        self.count = 0
        self.limit = 500000
