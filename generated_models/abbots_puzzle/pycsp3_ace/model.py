# abbots_puzzle: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python abbots_puzzle.py

from pycsp3 import *


def create_model(instance):
    """100 bushels of corn are distributed among 100 people: each man receives
    three bushels, each woman two and each child half a bushel, and there are
    five times as many women as men. Find the number of men, women and children."""
    n_people = 100
    n_bushels = 100

    # The number of men, women and children: between 0 and n_people each.
    men = Var(dom=range(n_people + 1))
    women = Var(dom=range(n_people + 1))
    children = Var(dom=range(n_people + 1))

    satisfy(
        # There are n_people people.
        men + women + children == n_people,
        # The bushels add up to n_bushels. Each man gets 3, each woman 2 and each child half a bushel,
        # so counted in half bushels a man is 6, a woman 4 and a child 1.
        6 * men + 4 * women + children == 2 * n_bushels,
        # There are five times as many women as men.
        women == 5 * men,
    )

    return {"men": men, "women": women, "children": children}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
