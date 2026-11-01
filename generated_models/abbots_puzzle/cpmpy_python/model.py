# abbots_puzzle: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install cpmpy`) with:
#   python abbots_puzzle.py

import cpmpy as cp


def create_model(instance):
    """100 bushels of corn are distributed among 100 people: each man receives
    three bushels, each woman two and each child half a bushel, and there are
    five times as many women as men. Find the number of men, women and children."""
    # The puzzle states all its numbers, so the instance holds no data.

    # The number of men, of women and of children
    men = cp.intvar(0, 100, name="men")
    women = cp.intvar(0, 100, name="women")
    children = cp.intvar(0, 100, name="children")

    model = cp.Model()
    # There are 100 people.
    model.add(men + women + children == 100)
    # The bushels add up to 100. Counted in half bushels (men 6, women 4,
    # children 1) so that all coefficients stay whole numbers: 200 half bushels.
    model.add(men * 6 + women * 4 + children == 200)
    # There are five times as many women as men.
    model.add(women == men * 5)

    return model, {"men": men, "women": women, "children": children}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
