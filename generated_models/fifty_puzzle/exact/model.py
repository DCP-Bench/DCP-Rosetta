# fifty_puzzle: an Exact (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python fifty_puzzle.py fifty_puzzle.json

from exact import Exact


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs:
    choose the dummies to knock down so that their numbers add up to exactly
    the target sum, neither more nor less."""
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must reach exactly
    values = instance["values"]          # values[i]: the number on dummy i
    n_dummies = len(values)              # the number of dummies

    solver = Exact()

    # Exact identifies its variables by name.
    # dummies[i] is 1 when dummy i is knocked over, and 0 when not
    dummies = [f"dummy_{i}" for i in range(n_dummies)]
    for name in dummies:
        solver.addVariable(name, 0, 1)

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    solver.addConstraint([(v, d) for v, d in zip(values, dummies) if v], True, target_sum, True, target_sum)

    return solver, {"dummies": dummies}


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
