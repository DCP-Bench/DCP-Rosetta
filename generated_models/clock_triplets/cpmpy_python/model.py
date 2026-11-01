# clock_triplets: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install cpmpy`) with:
#   python clock_triplets.py

import cpmpy as cp


def create_model(instance):
    """Rearrange the numbers on the face of a clock (1 to 12) so that no triplet of
    adjacent numbers has a sum higher than 21, the smallest value the highest
    triplet sum can have."""
    n = 12  # numbers on the clock face

    # x[i] is the number at position i of the clock face
    x = cp.intvar(1, n, shape=n, name="x")

    model = cp.Model()

    # Each number from 1 to 12 appears once on the clock.
    model.add(cp.AllDifferent(x))

    # Every three adjacent numbers, wrapping around the face, sum to at most 21.
    for i in range(n):
        model.add(x[i] + x[(i - 1) % n] + x[(i - 2) % n] <= 21)

    return model, {"x": x}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
