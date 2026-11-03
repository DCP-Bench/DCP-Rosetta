# among: a hermax (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install hermax`):
#   python among.py among.json

from hermax.model import Model


def create_model(instance):
    """Choose a value for each of n variables, each in 0..7, so that exactly m of the
    variables take a value from the list v. Other variables may take any value in 0..7."""
    n = instance["n"]              # n: how many variables x there are
    wanted = instance["m"]         # m: how many of them must take a value from v
    values = instance["v"]         # v: the set of values that count

    model = Model()

    # x[i] is the value of variable i, in 0..7 as the problem statement fixes
    x = model.int_vector("x", n, 0, 7)

    # A value listed twice in v counts once, and values outside 0..7 can never be taken.
    counted = sorted({value for value in values if 0 <= value <= 7})

    # Exactly m variables take a value from v. Each literal x[i] == value is true for at
    # most one value per variable, so the sum counts the variables that hit v.
    model &= (sum((x[i] == value) for i in range(n) for value in counted) == wanted)

    return model, {"x": x}


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
