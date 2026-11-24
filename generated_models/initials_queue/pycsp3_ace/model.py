# initials_queue: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python initials_queue.py

from pycsp3 import *


def create_model(instance):
    """The first 10 people in the queue for a Maths lecture each have initials that are an
    alphabetically ordered pair of distinct letters from the first five letters of the alphabet
    (A to E). No two people have the same initials, and no one shares a letter with the person in
    front of them. BE is at the front of the queue, CD right behind it, and BD at the end. Find the
    initials of the ten people, starting from the front."""
    n_people = 10
    letters = "ABCDE"  # the first five letters of the alphabet, the letters the initials use
    n_letters = len(letters)  # the number of letters in use
    letter_index = {letter: i for i, letter in enumerate(letters)}  # letter_index["A"] is 0, ..., letter_index["E"] is 4: the values the queue holds

    # queue[p][0] and queue[p][1] are the letters (0 for A to 4 for E) of the initials of the person at position p from the front
    queue = VarArray(size=[n_people, 2], dom=range(n_letters))

    satisfy(
        # The initials of each person are alphabetically ordered and distinct: the first letter comes before the second.
        [queue[p][0] < queue[p][1] for p in range(n_people)],
        # No two people have the same initials, so the pairs of letters are all different.
        AllDifferentList(queue),
        # No one shares a letter with the person in front: the four letters of two neighbours are all different.
        [AllDifferent(list(queue[p - 1]) + list(queue[p])) for p in range(1, n_people)],
        # BE is at the front of the queue, CD right behind it and BD at the end.
        [
            queue[0][0] == letter_index["B"], queue[0][1] == letter_index["E"],
            queue[1][0] == letter_index["C"], queue[1][1] == letter_index["D"],
            queue[n_people - 1][0] == letter_index["B"], queue[n_people - 1][1] == letter_index["D"],
        ],
    )

    return {"queue": queue}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        print("queue", "=")
        for row in outputs["queue"]:
            print(values(row))
    else:
        print("No solution:", status())
