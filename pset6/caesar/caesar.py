from sys import argv, exit
from cs50 import get_string

# Define main()


def main():
    check_args()
    k = int(argv[1])
    plaintext = get_string("plaintext: ")
    create_ciphertext(plaintext, k)
    print()


# Ensure the right number of command-line arguments were used


def check_args():
    if len(argv) != 2 or int(argv[1]) < 0 or not argv[1]:
        print("Usage: python caesar.py k")
        exit(1)


# Create and print ciphertext using ascii math via ord() and convert back to str with chr()


def create_ciphertext(plaintext, key):
    print("ciphertext: ", end="")
    for p in plaintext:
        if p.isupper():
            c = chr(ord('A') + (ord(p) - ord('A') + key) % 26)
            print(f"{c}", end="")
        elif p.islower():
            c = chr(ord('a') + (ord(p) - ord('a') + key) % 26)
            print(f"{c}", end="")
        else:
            print(f"{p}", end="")


if __name__ == "__main__":
    main()