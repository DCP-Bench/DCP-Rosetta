# broken_weights: a PyCSP3 model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python broken_weights.py broken_weights.json

from pycsp3 import *


def create_model(instance):
    """A merchant's measuring weight broke into n pieces, each a whole number of pounds,
    totalling m pounds. The pieces must weigh every whole number of pounds from 1 to m on
    a balance scale, where a piece may go on the same pan as the object or on the other pan.
    Find the weights of the pieces."""
    total_weight = instance["m"]   # m: the total weight of the broken measure, in pounds
    n_pieces = instance["n"]       # n: the number of pieces it broke into

    # weights[i] is the weight of piece i, a whole number of pounds
    weights = VarArray(size=n_pieces, dom=range(1, total_weight + 1))

    # pans[t][i] says where piece i goes when weighing t + 1 pounds:
    # 1 for the object's pan, -1 for the other pan, 0 for not used
    pans = VarArray(size=[total_weight, n_pieces], dom={-1, 0, 1})

    satisfy(
        # The pieces together weigh the whole measure.
        Sum(weights) == total_weight,
        # Every whole weight from 1 to m is balanced: the pieces on the object's pan
        # outweigh the pieces on the other pan by exactly that weight.
        [Sum(weights[i] * pans[target - 1][i] for i in range(n_pieces)) == target
         for target in range(1, total_weight + 1)],
    )

    return {"weights": weights}


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
