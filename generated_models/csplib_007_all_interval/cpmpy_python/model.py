# csplib_007_all_interval: a CPMpy model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

import cpmpy as cp


def create_model(instance):
    """Find a series of the pitch-classes 0 to n-1, each occurring once, in which the
    intervals between neighbouring notes cover every interval from 1 to n-1 once."""
    n = instance["n"]  # the number of pitch-classes (and so of notes in the series)

    # x[i] is the pitch-class of the note at position i
    x = cp.intvar(0, n - 1, shape=n, name="x")
    # diffs[i] is the interval between the notes at positions i and i + 1
    diffs = cp.intvar(1, n - 1, shape=n - 1, name="diffs")

    model = cp.Model()
    # The series is a permutation of the pitch-classes.
    model.add(cp.AllDifferent(x))
    # The intervals are a permutation of 1 to n-1.
    model.add(cp.AllDifferent(diffs))
    # Each interval is the distance between two neighbouring notes.
    model.add(diffs == cp.abs(x[1:] - x[:-1]))

    return model, {"x": x, "diffs": diffs}


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
