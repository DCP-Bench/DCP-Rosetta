# fifty_puzzle: a Z3 (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python fifty_puzzle.py fifty_puzzle.json

import z3


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs: choose the
    dummies to knock down so that their numbers add up to exactly the target sum, neither
    more nor less."""
    values = instance["values"]          # values[i] is the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must reach exactly

    # dummies[i] is true when dummy i is knocked over
    dummies = [z3.Bool(f"dummies_{i}") for i in range(len(values))]

    solver = z3.Solver()

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    solver.add(z3.PbEq([(d, v) for d, v in zip(dummies, values)], target_sum))

    return solver, {"dummies": dummies}


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
