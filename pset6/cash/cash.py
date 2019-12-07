from cs50 import get_float

# Define main()


def main():
    change = get_positive_float("Change owed: ")
    coins = get_coins(change)
    print(f"{coins}")

# Ensure change amount is positive and > 0


def get_positive_float(prompt):
    while True:
        change = get_float(prompt)
        if change > 0:
            # Round up for the math later
            change = change * 100
            return change

# Get number of coins by checking if we can remove the coin's value


def get_coins(change):
    coins = 0
    while change >= 25:
        change = change - 25
        coins += 1
    while change >= 10:
        change = change - 10
        coins += 1
    while change >= 5:
        change = change - 5
        coins += 1
    while change >= 1:
        change = change - 1
        coins += 1

    return coins


if __name__ == "__main__":
    main()