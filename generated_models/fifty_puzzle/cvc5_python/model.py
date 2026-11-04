# fifty_puzzle: a cvc5 (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python fifty_puzzle.py fifty_puzzle.json

import cvc5.pythonic as c5


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs:
    choose the dummies to knock down so that their numbers add up to exactly
    the target sum, neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must reach

    # dummies[i] is true when dummy i is knocked over
    dummies = [c5.Bool(f"dummies_{i}") for i in range(len(values))]

    solver = c5.Solver()

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    solver.add(c5.Sum([c5.If(d, v, 0) for v, d in zip(values, dummies)]) == target_sum)

    return solver, {"dummies": dummies}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
