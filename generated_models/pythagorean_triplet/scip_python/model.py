# pythagorean_triplet: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python pythagorean_triplet.py

from pyscipopt import Model


def create_model(instance):
    """Find three natural numbers a, b, c with a^2 + b^2 = c^2 (a Pythagorean
    triplet) and a + b + c = 1000. The instance file is empty ([]): the
    statement fixes the sum 1000, so the model reads nothing from the instance."""
    model = Model("pythagorean_triplet")

    # a, b, c are natural numbers. Natural numbers are taken to start at 1 (an
    # assumption about the statement's wording): with 0 allowed, (0, 500, 500)
    # would also be a solution. The constraints do not order a and b, so a
    # triplet and its reordering are both solutions.
    # The upper bound 998 is derived from the sum: the other two numbers are at
    # least 1 each, so each one is at most 1000 - 2.
    a = model.addVar(name="a", vtype="I", lb=1, ub=998)  # a leg of the right triangle
    b = model.addVar(name="b", vtype="I", lb=1, ub=998)  # the other leg
    c = model.addVar(name="c", vtype="I", lb=1, ub=998)  # the hypotenuse

    # a + b + c = 1000: the three numbers add up to 1000
    model.addCons(a + b + c == 1000)

    # a^2 + b^2 = c^2: the squares of the two shorter sides add up to the square
    # of the hypotenuse. Nonlinear, which SCIP handles as a nonlinear constraint.
    model.addCons(a**2 + b**2 == c**2)

    # No objective: the task is to find the triplet, so the model is a
    # satisfaction problem.
    return model, {"a": a, "b": b, "c": c}


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
