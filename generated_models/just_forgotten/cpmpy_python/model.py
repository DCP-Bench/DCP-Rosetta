# just_forgotten: a CPMpy model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python just_forgotten.py just_forgotten.json

import cpmpy as cp


def create_model(instance):
    """Joe forgot his bank account number. It has all the digits from 0 to n-1 in some
    order. In each set of digits he tried, exactly a given number of the digits were in
    their correct position. Find his account number."""
    guesses = instance["sets"]                # guesses[k][i]: digit i of the k-th number Joe tried
    correct = instance["num_correct_digits"]  # how many digits of each guess are in the right place
    n = len(guesses[0])

    # x[i] is digit i of the account number
    x = cp.intvar(0, n - 1, shape=n, name="x")

    model = cp.Model()

    # The account number has each digit from 0 to n-1 exactly once.
    model.add(cp.AllDifferent(x))

    # Each guess has exactly `correct` digits in the right position.
    for guess in guesses:
        model.add(cp.sum(x == guess) == correct)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
