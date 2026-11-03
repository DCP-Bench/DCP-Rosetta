# just_forgotten: a Z3 (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python just_forgotten.py just_forgotten.json

import z3


def create_model(instance):
    """Joe forgot his bank account number. It has all the digits from 0 to n-1 in some
    order. In each set of digits he tried, exactly a given number of the digits were in
    their correct position. Find his account number."""
    guesses = instance["sets"]                # guesses[k][i]: digit i of the k-th set of digits Joe tried
    correct = instance["num_correct_digits"]  # how many digits of each set are in the right position
    n_digits = len(guesses[0])

    # x[i] is digit i of the account number
    x = [z3.Int(f"x_{i}") for i in range(n_digits)]

    solver = z3.Solver()

    # Every digit is from 0 to n-1, and each digit appears once.
    solver.add([v >= 0 for v in x] + [v <= n_digits - 1 for v in x] + [z3.Distinct(x)])

    # Each set of digits has exactly `correct` digits in the right position.
    for guess in guesses:
        solver.add(z3.Sum([z3.If(x[i] == guess[i], 1, 0) for i in range(n_digits)]) == correct)

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
