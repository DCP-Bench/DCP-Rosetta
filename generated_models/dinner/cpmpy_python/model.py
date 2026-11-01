# dinner: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install cpmpy`) with:
#   python dinner.py

import cpmpy as cp


def create_model(instance):
    """Twenty people go to dinner, grandparents, parents and children, and the
    bill is $20: how many of each go?"""
    # Prices are in half dollars, so the child's $0.50 is an integer.
    # A grandparent costs $3, a parent $2 and a child $0.50.

    # The number of grandparents (1 to 6), parents (1 to 10) and children (1 to 40) at dinner
    grandparents = cp.intvar(1, 6, name="grandparents")
    parents = cp.intvar(1, 10, name="parents")
    children = cp.intvar(1, 40, name="children")

    model = cp.Model()
    # The dinner costs $20, which is 40 half dollars.
    model.add(grandparents * 6 + parents * 4 + children * 1 == 20 * 2)
    # There are 20 people in total.
    model.add(grandparents + parents + children == 20)

    return model, {"grandparents": grandparents, "parents": parents, "children": children}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
