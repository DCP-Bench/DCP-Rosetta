# pythagorean_triplet: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install cpmpy`) with:
#   python pythagorean_triplet.py

import cpmpy as cp


def create_model(instance):
    """Find the Pythagorean triplet a, b, c (natural numbers with a^2 + b^2 = c^2)
    whose three members add up to 1000. The statement fixes the data, so instance is empty."""
    # a, b and c are the three members of the triplet. Since they add up to 1000
    # and are positive, none can exceed 500 (c is the largest, and a + b > c).
    a, b, c = cp.intvar(1, 500, shape=3, name="x")

    model = cp.Model()
    # The three members add up to 1000.
    model.add(a + b + c == 1000)
    # The Pythagorean relation.
    model.add(a * a + b * b == c * c)

    return model, {"a": a, "b": b, "c": c}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
