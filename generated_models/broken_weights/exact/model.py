# broken_weights: an Exact (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python broken_weights.py broken_weights.json

from exact import Exact


def create_model(instance):
    """A merchant's measuring weight of a whole number of pounds broke into pieces, each a whole
    number of pounds. On a balance scale the pieces must weigh every whole load from 1 up to the
    total weight."""
    total = instance["m"]     # the weight of the unbroken weight, in pounds
    n_pieces = instance["n"]  # the number of pieces it broke into

    solver = Exact()

    # Exact identifies its variables by name.
    # weights[j] is the weight of piece j, in pounds
    weights = [f"weights_{j}" for j in range(n_pieces)]
    for name in weights:
        solver.addVariable(name, 1, total)

    # The pieces add up to the whole weight.
    solver.addConstraint([(1, name) for name in weights], True, total, True, total)

    # Each load from 1 to the total weight is balanced by the pieces.
    for load in range(1, total + 1):
        signed = []
        for j in range(n_pieces):
            # side is 1 when piece j is on the pan opposite the load, -1 when it is on the
            # load's pan, and 0 when it is off the scale
            side = f"side_{load}_{j}"
            solver.addVariable(side, -1, 1)
            # the weight of piece j with its side, in pounds
            term = f"term_{load}_{j}"
            solver.addVariable(term, -total, total)
            solver.addMultiplication([weights[j], side], True, term, True, term)
            signed.append((1, term))
        # The pieces on the opposite pan, less those on the load's pan, weigh the load.
        solver.addConstraint(signed, True, load, True, load)

    return solver, {"weights": weights}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
