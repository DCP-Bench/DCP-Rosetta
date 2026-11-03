# autoref: a hermax (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install hermax`):
#   python autoref.py autoref.json

from hermax.model import Model


def create_model(instance):
    """Find a series S = (s[0], s[1], ..., s[n+1]) in which every
    value i from 0 to n occurs exactly s[i] times (domain convention: values are restricted
    to 0..n, as in the reference formulation, not a stated requirement), and whose last element s[n+1] is m.
    The series is not empty, and s is its only output."""
    n = instance["n"]              # the largest value counted (values 0..n)
    last_value = instance["m"]     # the required value of the last element, s[n+1]

    model = Model()

    # s[k] is the k-th element of the series, a value restricted to 0..n as in the reference formulation; the series has n + 2 elements
    s = model.int_vector("s", n + 2, 0, n)

    # The last element of the series is m.
    model &= (s[n + 1] == last_value)

    # For each value i, the number of positions k at which the series holds i is s[i].
    for i in range(n + 1):
        model &= (sum(s[k] == i for k in range(n + 2)) == s[i])

    return model, {"s": s}


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
