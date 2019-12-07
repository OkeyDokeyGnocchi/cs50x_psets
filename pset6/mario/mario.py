from cs50 import get_int


def main():
    height = get_positive_int("Height: ")
    # After getting height, run for range starting at 1 (so add 1 to height to compensate)
    for i in range(1, height + 1):
        for j in range(height - i):
            print(" ", end="")
        for k in range(i):
            print("#", end="")
        print()

# Make sure height is positive and less than 8


def get_positive_int(prompt):
    while True:
        height = get_int(prompt)
        if height > 0 and height < 9:
            return height


main()
