# fifty_puzzle: a PyCSP3 model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python fifty_puzzle.py fifty_puzzle.json

from pycsp3 import *


def create_model(instance):
    """A side show has a number of little dummies, each with a number on it. Throw
    baseballs to knock dummies over; the numbers on the dummies knocked down must add up
    to exactly a given target sum, neither more nor less. Find which dummies are knocked over."""
    target_sum = instance["target_sum"]  # the sum the numbers of the knocked-over dummies must make exactly
    numbers = instance["values"]         # numbers[i] is the number on dummy i
    n_dummies = len(numbers)

    # knocked_over[i] is 1 when dummy i is knocked over, else 0
    knocked_over = VarArray(size=n_dummies, dom={0, 1})

    satisfy(
        # The numbers on the knocked-over dummies add up to exactly the target sum.
        Sum(numbers[i] * knocked_over[i] for i in range(n_dummies)) == target_sum,
    )

    return {"dummies": knocked_over}


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
