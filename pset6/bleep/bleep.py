from cs50 import get_string
from sys import argv, exit


def main():
    check_args()
    words = set()
    banned_list = argv[1]
    load(banned_list, words)
    tokens = get_uncensored("What message would you like to censor?\n")
    check(tokens, words)


# Check that number of arguments is correct


def check_args():
    if len(argv) != 2:
        print("Usage: python bleep.py dictionary")
        exit(1)


# Get the user's input for string to be censored


def get_uncensored(prompt):
    tokens = []
    uncensored = get_string(prompt)
    for word in uncensored.split(sep=' '):
        tokens.append(word)
    return tokens


# Check the words in the user's input against the banned list


def check(tokens, banned_list):
    for word in tokens:
        if word.lower() in banned_list:
            for i in range(len(word)):
                print("*", end="")
            print(" ", end="")
        else:
            print(f"{word}", end=" ")

    print()


# Load the words from the banned list file into memory


def load(banned_list, words_list):
    file = open(banned_list, "r")
    for word in file:
        words_list.add(word.rstrip("\n"))
    file.close()


if __name__ == "__main__":
    main()
