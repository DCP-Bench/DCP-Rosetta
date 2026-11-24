# session3_farmer_and_cows: a SCIP (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """A farmer has cows numbered 1 to num_cows, and each cow gives a quantity of
    milk equal to its number. He has num_sons sons and wants to give son s exactly
    cows_per_son[s] cows, so that every son gets the same total quantity of milk.
    Which son gets each cow?"""
    num_cows = instance["num_cows"]          # the number of cows, numbered 1 to num_cows
    num_sons = instance["num_sons"]          # the number of sons, numbered 0 to num_sons - 1
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: how many cows son s gets

    milk = np.arange(1, num_cows + 1)  # milk[c]: the milk cow c + 1 gives, which is its number
    total_milk = int(milk.sum())       # the milk of all cows together; no son's share can be more

    model = Model("farmer_and_cows")

    # x[c, s] is 1 when cow c + 1 goes to son s, and 0 when not
    x = model.addMatrixVar((num_cows, num_sons), vtype="B", name="x")

    # The quantity of milk each son gets, the same for every son. Its value is
    # total_milk / num_sons, forced by the constraints below: if the milk cannot be
    # split equally, the model has no solution.
    milk_per_son = model.addVar(vtype="I", lb=0, ub=total_milk, name="milk_per_son")

    # Each cow goes to exactly one son.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # Each son gets exactly the number of cows the distribution gives him.
    model.addMatrixCons(x.sum(axis=0) == np.array(cows_per_son))

    # Each son's cows give the same total milk, milk_per_son.
    model.addMatrixCons((milk @ x) == milk_per_son)

    # The output is the son of each cow: the son s for which x[c, s] is 1.
    return model, {"cow_assignments": x @ np.arange(num_sons)}


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
