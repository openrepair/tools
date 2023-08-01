import random
import string


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

