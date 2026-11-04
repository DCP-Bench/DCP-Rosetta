# just_forgotten: an Exact (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python just_forgotten.py just_forgotten.json

from exact import Exact


def create_model(instance):
    """Joe's account number uses each digit from 0 to n-1 once. Each set of digits he tried has
    a given number of its digits in the right position. Find the account number."""
    sets = instance["sets"]                        # sets[k][i]: the digit at position i in the k-th set Joe tried
    num_correct = instance["num_correct_digits"]   # how many digits of each set are in the right position
    n_digits = len(sets[0])                        # the number of digits in the account number

    solver = Exact()

    # Exact identifies its variables by name.
    # digit_at[i][d] is 1 when position i of the account number holds digit d, and 0 when not.
    digit_at = [[f"digit_{d}_at_{i}" for d in range(n_digits)] for i in range(n_digits)]
    for i in range(n_digits):
        for name in digit_at[i]:
            solver.addVariable(name, 0, 1)

    # x[i] is the digit at position i of the account number, from 0 to n-1.
    x = [f"x_{i}" for i in range(n_digits)]
    for name in x:
        solver.addVariable(name, 0, n_digits - 1)

    # Each position holds exactly one digit.
    for i in range(n_digits):
        solver.addConstraint([(1, name) for name in digit_at[i]], True, 1, True, 1)

    # Each digit is used at exactly one position.
    for d in range(n_digits):
        solver.addConstraint([(1, digit_at[i][d]) for i in range(n_digits)], True, 1, True, 1)

    # The digit at each position is the one marked in digit_at.
    for i in range(n_digits):
        solver.addConstraint([(d, digit_at[i][d]) for d in range(1, n_digits)] + [(-1, x[i])],
                             True, 0, True, 0)

    # Each set Joe tried has exactly num_correct digits in the same position as the account number.
    for tried in sets:
        solver.addConstraint([(1, digit_at[i][tried[i]]) for i in range(n_digits)],
                             True, num_correct, True, num_correct)

    return solver, {"x": x}


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
