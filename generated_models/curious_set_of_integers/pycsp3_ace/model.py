# curious_set_of_integers: a PyCSP3 model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python curious_set_of_integers.py curious_set_of_integers.json

from pycsp3 import *


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set with a remarkable property: the product of any two
    integers is one less than a perfect square. Find a fifth number (larger than or equal to 0)
    that can be added to the set without destroying this property."""
    max_val = instance["max_val"]    # the largest value the fifth number may take (the statement gives no bound, so this instance field is taken as one)
    # The field n, the size of the full set (four given integers and the fifth), is not read:
    # the statement fixes the four given integers below.
    given = [1, 3, 8, 120]           # the four integers the statement gives

    # number: the fifth number, between 0 and max_val
    number = Var(dom=range(max_val + 1))

    # root[i] is the square root of given[i] * number + 1, so that the product plus one is a square.
    # A root r of a value at most max_product satisfies r <= sqrt(max_product), so this range holds all of them.
    max_product = max(given) * max_val + 1
    root_bound = int(max_product ** 0.5) + 1
    root = VarArray(size=len(given), dom=range(root_bound + 1))

    satisfy(
        # The given integers already have the property with each other (for example 3 * 8 + 1 = 25),
        # so only the products of each given integer with the fifth number are constrained:
        # given[i] * number + 1 is a perfect square.
        [root[i] * root[i] == given[i] * number + 1 for i in range(len(given))]
    )

    return {"number": number}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
