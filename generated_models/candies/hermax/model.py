# candies: a hermax (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install hermax`):
#   python candies.py candies.json

from hermax.model import Model


def create_model(instance):
    """Alice gives every child in a line at least one candy, gives a child with a higher
    rating than a neighbour more candies than that neighbour, and wants the total number
    of candies to be as small as possible."""
    ratings = instance["ratings"]  # ratings[i]: the rating score of child i
    n = len(ratings)               # the number of children

    m = Model()

    # candies[i] is the number of candies child i gets. The upper bound n is implied by
    # the problem: a run of children each rated higher than the one before needs at most
    # n candies, so no child can need more than n.
    candies = m.int_vector("candies", n, 1, n)

    # A child with a higher rating than a neighbour gets more candies than that neighbour.
    # Neighbours with equal ratings have no constraint between them.
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            m &= (candies[i] >= candies[i + 1] + 1)
        elif ratings[i] < ratings[i + 1]:
            m &= (candies[i + 1] >= candies[i] + 1)

    # z is the total number of candies handed out.
    total = sum(candies)

    # Minimise the total number of candies.
    m.obj += total

    # The objective in the problem's terms: the total number of candies, the cost minimised above.
    return m, {"x": candies, "z": total}, total


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
