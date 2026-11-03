# among: a Z3 (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python among.py among.json

import z3


def create_model(instance):
    """Exactly m of the n values in x take one of the numbers in v. Every value in x
    is between 0 and 7."""
    n = instance["n"]  # the number of values in x
    m = instance["m"]  # how many values in x must be one of the numbers in v
    v = instance["v"]  # the numbers that count

    # x[i] is the i-th value.
    x = [z3.Int(f"x_{i}") for i in range(n)]

    solver = z3.Solver()

    # Every value in x is between 0 and 7.
    solver.add([z3.And(0 <= xi, xi <= 7) for xi in x])

    # counted[i] is 1 when the i-th value is one of the numbers in v, else 0.
    counted = [z3.If(z3.Or([xi == number for number in v]), 1, 0) for xi in x]
    # Exactly m values in x are one of the numbers in v.
    solver.add(z3.Sum(counted) == m)

    return solver, {"x": x}


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
