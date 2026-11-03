# csplib_007_all_interval: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

from hermax.model import Model


def create_model(instance):
    """All-interval series: arrange the pitch classes 0..n-1 in a sequence, each used
    exactly once, so that the absolute differences between neighbouring pitch classes
    are exactly the intervals 1..n-1, each occurring once."""
    n = instance["n"]  # n: the number of pitch classes, and the length of the series

    m = Model()

    # x[i] is the pitch class played at position i of the series, a value in 0..n-1
    x = m.int_vector("x", n, 0, n - 1)
    # diffs[i] is the interval between the pitch classes at positions i and i+1, in 1..n-1
    diffs = m.int_vector("diffs", n - 1, 1, n - 1)

    # Every pitch class occurs exactly once in the series.
    m &= x.all_different()
    # Every interval from 1 to n-1 occurs exactly once among the neighbouring pairs.
    m &= diffs.all_different()

    # The interval between neighbours is the absolute difference of their pitch classes:
    # for every ordered pair of distinct pitch classes (a, b) at positions i and i+1,
    # the interval at position i must be |a - b|. Written as one clause per pair of values,
    # not as a half-reified sum nor as one m.table([x[i], x[i+1], diffs[i]], rows) per
    # position. Measured at n=20: the half-reified form found nothing in 180 s, and the
    # per-position table did not finish in 180 s either, while these clauses tie the
    # one-hot literals of x and diffs directly and the whole check takes about 7 s.
    for i in range(n - 1):
        for a in range(n):
            for b in range(n):
                if a != b:
                    m &= ~(x[i] == a) | ~(x[i + 1] == b) | (diffs[i] == abs(a - b))

    return m, {"x": x, "diffs": diffs}


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
