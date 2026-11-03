# bowls_and_oranges: a hermax (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install hermax`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from hermax.model import Model


def create_model(instance):
    """Place all the oranges in bowls set in a line at 1 metre intervals, at most one orange
    per bowl, so that no three oranges A, B, C have the distance between A and B equal to
    the distance between B and C. Report the bowls used, in ascending order."""
    bowls = instance["n"]    # n: the number of bowls, numbered 1 to n along the line
    oranges = instance["m"]  # m: the number of oranges to place

    m = Model()

    # x[i] is the bowl (1 to n) of the i-th orange, numbered so the bowls ascend
    x = m.int_vector("x", oranges, 1, bowls)
    # One orange per bowl: the bowls are strictly ascending, so no two share a bowl.
    for i in range(oranges - 1):
        m &= (x[i] < x[i + 1])

    # No three oranges at equal distances. As x is strictly ascending, only i < j < k matters:
    # x[j] - x[i] != x[k] - x[j], i.e. x[i] + x[k] != 2 * x[j].
    for i in range(oranges):
        for j in range(i + 1, oranges):
            for k in range(j + 1, oranges):
                m &= (x[i] + x[k] != 2 * x[j])

    # There is no objective: any placement that satisfies the rules is a solution.
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
