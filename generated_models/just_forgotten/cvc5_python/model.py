# just_forgotten: a cvc5 (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python just_forgotten.py just_forgotten.json

import cvc5.pythonic as c5


def create_model(instance):
    """Joe forgot his bank account number. It has the digits from 0 to n-1 in some order.
    For each set of digits he tried, exactly a given number of digits were in their correct
    position. Find his account number."""
    guesses = instance["sets"]  # the sets of digits Joe tried, each a permutation of 0 to n-1
    n_correct = instance["num_correct_digits"]  # how many digits of each set are in the right position
    n_digits = len(guesses[0])  # the number of digits in the account number

    # x[i]: the digit at position i of the account number
    x = [c5.Int(f"x_{i}") for i in range(n_digits)]

    # the conditions the account number must meet
    solver = c5.Solver()

    # Every digit is between 0 and n_digits - 1.
    for digit in x:
        solver.add(digit >= 0, digit <= n_digits - 1)

    # The account number has each digit from 0 to n_digits - 1 exactly once.
    solver.add(c5.Distinct(x))

    # Each set of digits Joe tried has exactly n_correct digits in the right position.
    for guess in guesses:
        solver.add(c5.Sum([c5.If(xi == g, 1, 0) for xi, g in zip(x, guess)]) == n_correct)

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
