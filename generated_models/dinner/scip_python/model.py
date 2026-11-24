# dinner: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python dinner.py

from pyscipopt import Model


def create_model(instance):
    """Choose how many grandparents, parents and children go out to dinner.

    The instance file is empty ([]), so the instance argument is not read: the
    data is fixed by the statement. The group sizes are integers within the
    statement's ranges, 20 people must go, and the dinner must cost $20.
    This is a satisfaction problem: any assignment meeting these is an answer.
    """
    model = Model("dinner")

    # The number of grandparents going, 1 to 6 (the statement's range).
    grandparents = model.addVar("grandparents", vtype="I", lb=1, ub=6)
    # The number of parents going, 1 to 10 (the statement's range).
    parents = model.addVar("parents", vtype="I", lb=1, ub=10)
    # The number of children going, 1 to 40 (the statement's range).
    children = model.addVar("children", vtype="I", lb=1, ub=40)

    # There must be 20 people at dinner.
    model.addCons(grandparents + parents + children == 20)

    # The dinner must cost $20. Counting in half dollars keeps the coefficients
    # integers: a grandparent costs $3 = 6 half dollars, a parent $2 = 4 half
    # dollars, a child $0.50 = 1 half dollar, and $20 = 40 half dollars.
    model.addCons(6 * grandparents + 4 * parents + children == 40)

    return model, {"grandparents": grandparents, "parents": parents, "children": children}


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
