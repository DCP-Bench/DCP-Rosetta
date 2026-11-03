# fifty_puzzle: a SCIP (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python fifty_puzzle.py fifty_puzzle.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """A side show: each dummy has a number written on it, and the player may
    throw as many balls as they like at a cent apiece. Choose which dummies to
    knock over so that the numbers on the knocked-over dummies add up to exactly
    the target sum, neither more nor less. The output dummies[i] is True when
    dummy i is knocked over."""
    values = instance["values"]      # values[i]: the number written on dummy i
    target = instance["target_sum"]  # the exact sum the numbers on the knocked-over dummies must add up to

    model = Model("fifty_puzzle")

    # knocked[i] is 1 when dummy i is knocked over, and 0 when it is left standing
    knocked = [model.addVar(f"knocked_{i}", vtype="B") for i in range(len(values))]

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    model.addCons(quicksum(v * k for v, k in zip(values, knocked)) == target)

    # Satisfaction problem: no objective, any choice that reaches the target is a solution.
    return model, {"dummies": knocked}


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
