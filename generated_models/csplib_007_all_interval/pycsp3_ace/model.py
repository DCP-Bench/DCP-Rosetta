# csplib_007_all_interval: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

from pycsp3 import *


def create_model(instance):
    """Given the n pitch-classes 0, 1, ..., n-1, find a series s = (s_1, ..., s_n) that is a
    permutation of 0..n-1 and whose interval vector (|s_2 - s_1|, ..., |s_n - s_{n-1}|) is a
    permutation of 1..n-1."""
    n = instance["n"]  # the number of pitch-classes, and of notes in the series
    n_intervals = n - 1  # the number of neighbouring pairs of notes

    # x[i] is the pitch-class of note i in the series
    x = VarArray(size=n, dom=range(n))
    # diffs[i] is the interval between note i and note i + 1; the intervals are a permutation of 1..n-1, so each lies in that range
    diffs = VarArray(size=n_intervals, dom=range(1, n))

    satisfy(
        # each pitch-class occurs exactly once
        AllDifferent(x),
        # each interval from 1 to n-1 occurs exactly once
        AllDifferent(diffs),
        # the interval between neighbouring notes is the distance between their pitch-classes
        [diffs[i] == abs(x[i + 1] - x[i]) for i in range(n_intervals)],
    )

    return {"x": x, "diffs": diffs}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
