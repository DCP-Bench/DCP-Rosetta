# giant_cat_army: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python giant_cat_army.py

from pycsp3 import *


def create_model(instance):
    """Start with the list [0] and build a longer list, each step either adding 5, adding 7
    or taking the square root (which must be an integer). Find a list of 24 integers that
    starts with 0, ends with 14, contains 2, 10 and 14 in that order (other numbers may lie
    between them), has all elements distinct, all at most 60 and all integers."""
    start = 0  # the list starts with 0
    goal = 14  # the list ends with 14
    length = 24  # the list has 24 elements
    max_value = 60  # every element is at most 60
    required = [2, 10, 14]  # these numbers appear in the list in this order
    steps = [5, 7]  # the amounts the game lets you add, 5 and 7 as the description says

    # x[i] is the i-th element of the list, from 0 to max_value
    x = VarArray(size=length, dom=range(max_value + 1))

    # pos[k] is the position in the list of the k-th required number
    pos = VarArray(size=len(required), dom=range(length))

    # The steps the game allows, as pairs (a, b) where b follows a: adding 5 or 7, or taking the
    # square root of a, which is an integer exactly when b * b == a
    transitions = [
        (a, b)
        for a in range(max_value + 1)
        for b in range(max_value + 1)
        if b - a in steps or b * b == a
    ]

    satisfy(
        # The list starts with 0.
        x[0] == start,
        # Each element follows the one before it by one of the allowed steps.
        [Table(scope=[x[i], x[i + 1]], supports=transitions) for i in range(length - 1)],
        # The list ends with 14.
        x[length - 1] == goal,
        # The elements are all distinct.
        AllDifferent(x),
        # The k-th required number sits at pos[k] in the list.
        [x[pos[k]] == required[k] for k in range(len(required))],
        # The positions of 2, 10 and 14 increase, so the numbers appear in that order.
        Increasing(pos, strict=True),
    )

    return {"x": x}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
