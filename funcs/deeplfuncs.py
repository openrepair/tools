import os
import deepl
import random
import string


# Wrap/mock DeepL calls.
class deeplWrapper:
    # Vast majority of English problem text is British, currently.
    # Fixit Clinic is only US English, too few to make a case for 'en-us' just yet.
    # There are a few Danish (DNK) records in the dataset, so will need 'da' before long.
    langs = ['en-gb', 'de', 'nl', 'fr', 'it', 'es']
    def __init__(self, mock=False):
        if mock:
            self.translator = mockDeepLTranslator()
        else:
            if auth_key := self.get_key():
                self.translator = deepl.Translator(auth_key)
            else:
                self.translator = False
                print('Add your DeepL API key to the .env file.')

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

    def get_key():
        if 'DEEPL_KEY' in os.environ:
            return os.environ['DEEPL_KEY']
        else:
            print('ERROR! DEEPL_KEY NOT FOUND!')
            return False


# To Do: mock exception
class mockDeepLTranslator:

    def translate_text(self, text, target_lang, source_lang=''):
        self.detected_source_lang = mockDeepLTranslator.mockTranslation(len=2, up=True)
        self.text = mockDeepLTranslator.mockTranslation()
        return self

    def get_usage(self):
        return mockDeepLUsage()

    @staticmethod
    def mockTranslation(len=0, lo=False, up=False, ws=False, nums=False, punct=False):
        if len == 0:
            len = random.randint(6,12)

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

