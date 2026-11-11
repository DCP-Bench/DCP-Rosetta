# cur_num: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python cur_num.py

from pycsp3 import *


def create_model(instance):
    """The number 48 has this peculiarity, that if you add 1 to it the result is a square
    number, and if you add 1 to its half, you also get a square number. Find another number
    with this peculiarity between 1 and 10000."""
    max_number = 10000  # the answer lies between 1 and max_number
    example = 48        # the number the statement gives; the answer must be another one
    max_root = int((max_number + 1) ** 0.5) + 1  # one more than the integer square root of max_number + 1: every square root needed is at most that

    # peculiar: the number sought, between 1 and max_number.
    peculiar = Var(dom=range(1, max_number + 1))
    # half: half of peculiar, which must be a whole number (assumed: the statement speaks of its half).
    half = Var(dom=range(1, max_number // 2 + 1))
    # square_root: the square root of peculiar + 1.
    square_root = Var(dom=range(max_root + 1))
    # half_root: the square root of half + 1.
    half_root = Var(dom=range(max_root + 1))

    satisfy(
        # The answer is another number, not 48 itself.
        peculiar != example,
        # Adding 1 to the number gives a square number.
        square_root * square_root == peculiar + 1,
        # The number is even, so that its half is a whole number (assumed, as above).
        peculiar == 2 * half,
        # Adding 1 to its half gives a square number.
        half_root * half_root == half + 1,
    )

    return {"peculiar": peculiar}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
