# four_numbers: a PyCSP3 model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python four_numbers.py four_numbers.json

from pycsp3 import *


def create_model(instance):
    """Given a list of up to four distinct integers between 1 and 10, find three integers
    (also between 1 and 10) such that every given number is a sum of some of the three."""
    numbers = instance["numbers"]  # the given numbers
    max_value = 10  # the bound the statement gives on the given numbers and on the three integers
    n_picks = 3  # the number of integers to find

    # x[j] is the j-th of the three integers to find
    x = VarArray(size=n_picks, dom=range(1, max_value + 1))

    # picked[i][j] is 1 when the j-th integer is part of the sum that makes numbers[i]
    picked = VarArray(size=[len(numbers), n_picks], dom={0, 1})

    satisfy(
        # Each given number is the sum of a subset of the three integers.
        Sum(picked[i][j] * x[j] for j in range(n_picks)) == numbers[i]
        for i in range(len(numbers))
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
