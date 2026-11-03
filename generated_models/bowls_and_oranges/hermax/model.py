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

    # occupied[p - 1] is true when bowl p holds an orange
    occupied = m.bool_vector("occupied", bowls)
    # Every orange's bowl is an occupied bowl.
    for i in range(oranges):
        for p in range(1, bowls + 1):
            m &= (~(x[i] == p) | occupied[p - 1])
    # Exactly one orange per bowl, so exactly `oranges` bowls are occupied; together with
    # the previous constraint, the occupied bowls are exactly the bowls the oranges use.
    m &= (sum(occupied[p] for p in range(bowls)) == oranges)

    # No three oranges at bowls p < p + d < p + 2d (equal distances): these three bowls
    # are never all occupied.
    for p in range(1, bowls + 1):
        for d in range(1, (bowls - p) // 2 + 1):
            m &= (~occupied[p - 1] | ~occupied[p + d - 1] | ~occupied[p + 2 * d - 1])

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
