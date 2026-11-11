# three_coins: a PyCSP3 model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python three_coins.py three_coins.json

from pycsp3 import *


def create_model(instance):
    """Three coins lie on a table in the order tails, heads, tails. In precisely three
    moves make them face either all heads or all tails. Each move consists of choosing
    one coin and flipping it over."""
    init = instance["init"]  # init[i] is 1 when coin i starts tails up, 0 when heads up
    n_moves = instance["num_moves"]  # the number of moves to make
    n_coins = len(init)

    # steps[k][i] is 1 when coin i shows tails after k moves (steps[0] is the start)
    steps = VarArray(size=[n_moves + 1, n_coins], dom={0, 1})

    satisfy(
        # The first configuration is the initial one.
        [steps[0][i] == init[i] for i in range(n_coins)],
        # Each move flips exactly one coin, so exactly one position differs from the previous configuration.
        [Hamming(steps[k - 1], steps[k]) == 1 for k in range(1, n_moves + 1)],
        # The last configuration has all coins face the same way.
        AllEqual(steps[n_moves]),
    )

    return {"steps": steps}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("steps", "=")
        for row in outputs["steps"]:
            print(values(row))
    else:
        print("No solution:", status())
