# bales_of_hay: a Z3 (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python bales_of_hay.py bales_of_hay.json

import itertools

import z3


def create_model(instance):
    """Bales of hay were weighed in all possible pairs, and the pair weights were
    written down in numerical order without saying which pair gave which weight.
    Find the weight of each bale."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the weight of each pair of bales, in numerical order

    # bales[i] is the weight of bale i
    bales = [z3.Int(f"bale_{i}") for i in range(n)]

    solver = z3.Solver()

    # Every bale weighs between 0 and 50.
    solver.add([z3.And(0 <= b, b <= 50) for b in bales])

    # Each written weight is the total weight of some pair of different bales.
    solver.add([z3.Or([bales[i] + bales[j] == weight
                       for i, j in itertools.combinations(range(n), 2)])
                for weight in weights])

    return solver, {"bales": bales}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
