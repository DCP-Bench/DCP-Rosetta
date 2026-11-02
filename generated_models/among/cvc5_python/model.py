# among: a cvc5 (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python among.py among.json

import cvc5.pythonic as c5


def create_model(instance):
    """Exactly m of the values in x take one of the values in v. Every value in x
    is at least 0 and at most 7."""
    n = instance["n"]  # the number of values in x
    m = instance["m"]  # how many values in x must take a value from v
    v = instance["v"]  # the values that are counted

    # x[i] is the i-th value, from 0 to 7.
    x = [c5.Int(f"x_{i}") for i in range(n)]

    solver = c5.Solver()

    # Every value in x is from 0 to 7.
    solver.add([xi >= 0 for xi in x] + [xi <= 7 for xi in x])

    if not x or not v:
        # Nothing can take a value from v, so exactly m matches means m is 0.
        solver.add(c5.BoolVal(m == 0))
    else:
        # The distinct values in v, each counted once.
        counted = set(v)

        # Exactly m values in x take one of the values in v.
        solver.add(c5.Sum([c5.If(xi == value, 1, 0) for xi in x for value in counted]) == m)

    return solver, {"x": x}


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
