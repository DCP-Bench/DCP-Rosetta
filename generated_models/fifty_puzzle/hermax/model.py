# fifty_puzzle: a hermax (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install hermax`):
#   python fifty_puzzle.py fifty_puzzle.json

from hermax.model import Model


def create_model(instance):
    """Knock over some of the dummies so that the numbers painted on the fallen
    dummies add up to exactly the target sum. A satisfaction problem: any such
    choice is an answer."""
    target_sum = instance["target_sum"]  # the sum the knocked-over dummies must reach exactly
    values = instance["values"]          # values[i]: the number painted on dummy i
    n = len(values)                      # the number of dummies

    m = Model()
    # dummies[i] is true when dummy i is knocked over
    dummies = m.bool_vector("dummies", n)

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    m &= (sum(values[i] * dummies[i] for i in range(n)) == target_sum)

    return m, {"dummies": dummies}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
