# devils_word: a PyCSP3 model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python devils_word.py devils_word.json

from pycsp3 import *


def create_model(instance):
    """Given an array of integers, insert '+' or '-' operators before each integer in the array
    so that summing them up will result in a given total (666 for the devil's word)."""
    numbers = instance["arr"]    # numbers[i]: the i-th integer of the array
    total = instance["total"]    # the value the signed numbers must add up to
    n_numbers = len(numbers)

    # result[i] is numbers[i] with its sign: either +numbers[i] or -numbers[i]
    result = VarArray(size=n_numbers, dom=lambda i: {-numbers[i], numbers[i]})

    # The signed numbers add up to the total.
    satisfy(Sum(result) == total)

    return {"result": result}


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
