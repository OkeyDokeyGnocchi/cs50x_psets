from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""

    matches = []

    # Split lines by newline char and iterate through them
    for line in a.split("\n"):
        # If line is in both a & b and not already in matches append
        if line == "\n" and line in b and line not in matches:
            matches.append("")
        elif line in b and line not in matches:
            matches.append(line.rstrip("\n"))

    return matches


def sentences(a, b):
    """Return sentences in both a and b"""

    matches = []

    # Use nltk.tokenize.sent_tokenize to split by sentences
    sentenced_a = sent_tokenize(a, language='english')
    sentenced_b = sent_tokenize(b, language='english')

    # Iterate through sentences in a to check for matches in b, add matches to matches[]
    for sentence in sentenced_a:
        if sentence in sentenced_b and sentence not in matches:
            matches.append(sentence)

    return matches


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    matches = []

    # Iterate through a by length
    for i in range(len(a)):

        # Create substring_a by slicing a[position:n+position]
        substring_a = a[i:n+i]

        # Ensure that only substrings of length n are included
        if len(substring_a) == n:

            # If the substring is also in b and !in matches, append
            if substring_a in b and substring_a not in matches:
                matches.append(substring_a)

    return matches
