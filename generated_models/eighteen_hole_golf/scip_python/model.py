# eighteen_hole_golf: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python eighteen_hole_golf.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Generate an 18-hole golf course in which every hole is 3, 4 or 5 long
    and the total length of the course is 72.

    The instance file is empty ([]), so the statement fixes every number:
    18 holes, lengths from 3 to 5, and a total of 72. The instance argument is
    not read. The model is a satisfaction problem with no objective."""
    num_holes = 18        # the course has 18 holes
    shortest = 3          # the shortest hole the statement allows
    longest = 5           # the longest hole the statement allows
    total_length = 72     # the total length of the course

    model = Model("eighteen_hole_golf")

    # holes[i] is the length of hole i, a whole number from 3 to 5.
    # The bounds are the statement's lengths, so no separate constraint is needed.
    holes = [model.addVar(f"hole_{i}", vtype="I", lb=shortest, ub=longest)
             for i in range(num_holes)]

    # The lengths of the 18 holes add up to the total length of the course.
    model.addCons(quicksum(holes) == total_length)

    return model, {"holes": holes}


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
