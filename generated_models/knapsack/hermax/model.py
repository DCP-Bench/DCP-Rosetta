# knapsack: a hermax (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install hermax`):
#   python knapsack.py knapsack.json

from hermax.model import Model


def create_model(instance):
    """A hiker chooses which items to put in a backpack. Each item has a value and a weight.
    The items taken must weigh no more than the backpack's capacity, and the hiker wants
    the total value of the items taken to be as large as possible."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry
    n = len(values)                  # the number of items

    m = Model()

    # x[i] is true when the hiker takes item i into the backpack
    x = m.bool_vector("x", n)

    # The total weight of the items taken is at most the capacity.
    m &= (sum(weights[i] * x[i] for i in range(n)) <= capacity)

    # Maximise the total value taken. The objective is always minimised,
    # so minimise the negated total value.
    m.obj += -sum(values[i] * x[i] for i in range(n))

    return m, {"x": x}


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
