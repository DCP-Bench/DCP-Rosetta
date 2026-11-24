# abbots_puzzle: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python abbots_puzzle.py

from pyscipopt import Model


def create_model(instance):
    """Abbot's puzzle: 100 bushels of corn are distributed among 100 people,
    so that each man receives three bushels, each woman two, and each child
    half a bushel, and there are five times as many women as men. Find the
    number of men, women and children.

    The statement fixes every number, so the instance is empty and its
    argument is not read."""
    people = 100        # the number of people who receive corn, from the statement
    bushels = 100       # the bushels of corn distributed, from the statement
    women_per_man = 5   # there are five times as many women as men, from the statement

    model = Model("abbots_puzzle")

    # men is the number of men; at most all 100 people, from the statement
    men = model.addVar(name="men", vtype="I", lb=0, ub=people)
    # women is the number of women; at most all 100 people, from the statement
    women = model.addVar(name="women", vtype="I", lb=0, ub=people)
    # children is the number of children; at most all 100 people, from the statement
    children = model.addVar(name="children", vtype="I", lb=0, ub=people)

    # Everyone who receives corn is a man, a woman or a child.
    model.addCons(men + women + children == people)

    # Each man receives 3 bushels, each woman 2 and each child 1/2 bushel, and
    # together they receive all the corn. The equation is doubled so that every
    # coefficient is an integer: 6 per man, 4 per woman, 1 per child, and 2 * 100.
    model.addCons(6 * men + 4 * women + children == 2 * bushels)

    # There are five times as many women as men.
    model.addCons(women == women_per_man * men)

    # The statement asks for a satisfaction problem, so no objective is set.
    return model, {"children": children, "men": men, "women": women}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
