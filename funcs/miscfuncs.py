import random
import string
import json


# Put together an "OR" regex string pattern from a list of lowercase terms.
# With optional prefix/suffix captures of minimum length multilingual words.
def build_regex_string(terms, pre=True, aft=True):
    result = '(?i)('
    if (pre == True):
        result += '([a-zß-ÿœ]{3,}[ -]?)?'
    if (len(terms) > 0):
        result += '(' + '|'.join(list(set(terms))) + ')'
    if (aft == True):
        result += '([a-zß-ÿœ]{3,}[ -]?)?'
    result += ')'
    return result


def randstr(len=0, lo=False, up=False, ws=False, nums=False, punct=False):
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

