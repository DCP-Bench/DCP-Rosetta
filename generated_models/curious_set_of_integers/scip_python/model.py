# curious_set_of_integers: a SCIP (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

from math import isqrt

from pyscipopt import Model

# The four integers the statement gives. Every pair among them already has the
# property (1*3+1=4, 1*8+1=9, 1*120+1=121, 3*8+1=25, 3*120+1=361, 8*120+1=961),
# so the fifth number only has to pair up with each of them.
GIVEN = [1, 3, 8, 120]


def create_model(instance):
    """Find a number x >= 0 that can join the set 1, 3, 8, 120: the product of x
    with each of these integers is one less than a perfect square, that is,
    a * x + 1 is a perfect square for every given integer a. The model reports x."""
    # The largest value the answer x may take. It is the instance's max_val: the
    # statement gives no upper bound, so the search range comes from the data.
    max_val = instance["max_val"]
    # The instance field n (5) is the size of the completed set: the four given
    # integers plus the answer. The statement fixes the four, so the model does not read n.

    model = Model("curious_set_of_integers")

    # x is the fifth number, an integer from 0 to max_val
    x = model.addVar(name="x", vtype="I", lb=0, ub=max_val)

    # For each given integer a, the product a * x is one less than a perfect square:
    # a * x + 1 == r * r for an integer r >= 0, where r_a is the square root of a * x + 1.
    # The bound on r_a follows from r * r = a * x + 1 <= a * max_val + 1.
    for a in GIVEN:
        r = model.addVar(name=f"r_{a}", vtype="I", lb=0, ub=isqrt(a * max_val + 1))
        model.addCons(r * r == a * x + 1)

    # The problem has no objective: any x that passes every constraint is an answer.
    return model, {"number": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
