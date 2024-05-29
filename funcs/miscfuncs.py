import random
import string


# Interactive function execution.
def exec_opt(funcs):

    options = {0: "exit()"}
    print("{} : {}".format(0, "exit()"))
    for i in range(0, len(funcs)):
        options[i + 1] = funcs[i]
        print(f"{i + 1} : {funcs[i]}")

    choice = input("Type a number: ")

    try:
        choice = int(choice)
    except ValueError:
        print("Invalid choice")

    if choice >= len(options):
        print("Out of range")
    else:
        f = options[choice]
        print(f"Executing {f}")
        return f


def randstr(len=0, lo=False, up=False, ws=False, nums=False, punct=False):
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
    return "".join(random.choice(chars) for i in range(len))
