# just_forgotten: a PyCSP3 model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python just_forgotten.py just_forgotten.json

from pycsp3 import *


def create_model(instance):
    """Joe forgot one of his account numbers. It has all the digits from 0 to n-1 in some order. Joe tried
    several sets of digits, and in each set just a specific number of the digits were in their correct
    position. Find Joe's account number."""
    sets = instance["sets"]  # sets[s][i] is the digit in position i of the s-th set of digits Joe tried
    num_correct_digits = instance["num_correct_digits"]  # the number of digits in their correct position in each set
    n_digits = len(sets[0])

    # x[i] is the digit in position i of the account number
    x = VarArray(size=n_digits, dom=range(n_digits))

    satisfy(
        # The account number has the digits from 0 to n_digits - 1, each exactly once.
        AllDifferent(x),
        # In each set Joe tried, exactly num_correct_digits positions hold the same digit as the account number.
        [Sum(x[i] == digit for i, digit in enumerate(attempt)) == num_correct_digits for attempt in sets],
    )

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
