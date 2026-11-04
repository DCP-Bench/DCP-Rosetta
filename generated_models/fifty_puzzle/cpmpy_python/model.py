# fifty_puzzle: a CPMpy model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python fifty_puzzle.py fifty_puzzle.json

import cpmpy as cp


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs:
    choose the dummies to knock down so that their numbers add up to exactly
    the target sum, neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must reach

    # dummies[i] is true when dummy i is knocked over
    dummies = cp.boolvar(shape=len(values), name="dummies")

    model = cp.Model()
    # The numbers on the knocked-over dummies add up to exactly the target sum.
    model.add(cp.sum(dummies * values) == target_sum)

    return model, {"dummies": dummies}


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
