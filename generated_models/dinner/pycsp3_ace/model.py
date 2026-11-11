# dinner: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python dinner.py

from pycsp3 import *


def create_model(instance):
    """We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children.
    Grandparents cost $3 for dinner, parents $2 and children $0.50. There must be 20 total
    people at dinner and it must cost $20. How many grandparents, parents and children are
    going to dinner?"""
    # Money is counted in cents, so that every price is a whole number.
    grandparent_price = 300      # $3 per grandparent, in cents
    parent_price = 200           # $2 per parent, in cents
    child_price = 50             # $0.50 per child, in cents
    total_cost = 2000            # the dinner costs $20, in cents
    total_people = 20            # the number of people at dinner

    # The most of each kind of guest the statement allows.
    max_grandparents = 6
    max_parents = 10
    max_children = 40

    # grandparents: the number of grandparents going to dinner (1 to max_grandparents)
    grandparents = Var(dom=range(1, max_grandparents + 1))
    # parents: the number of parents going to dinner (1 to max_parents)
    parents = Var(dom=range(1, max_parents + 1))
    # children: the number of children going to dinner (1 to max_children)
    children = Var(dom=range(1, max_children + 1))

    satisfy(
        # There must be 20 total people at dinner.
        grandparents + parents + children == total_people,
        # The dinner must cost $20.
        grandparent_price * grandparents + parent_price * parents + child_price * children == total_cost,
    )

    return {"grandparents": grandparents, "parents": parents, "children": children}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
