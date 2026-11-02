# csplib_007_all_interval: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

import cvc5.pythonic as c5


def at_most_one(flags):
    """Constraints saying that at most one of the flags is true."""
    return [c5.Or(c5.Not(a), c5.Not(b)) for j, a in enumerate(flags) for b in flags[j + 1:]]


def exactly_one(flags):
    """Constraints saying that exactly one of the flags is true."""
    return [c5.Or(flags)] + at_most_one(flags)


def create_model(instance):
    """Arrange the pitch-classes 0 to n - 1 in a series, each used once, so that the intervals
    between neighbouring notes are the numbers 1 to n - 1, each used once."""
    n = instance["n"]  # the number of pitch-classes, and so of notes in the series
    m = n - 1  # the number of neighbouring pairs of notes, and of intervals

    # x[i] is the pitch-class of the note at position i
    x = [c5.Int(f"x_{i}") for i in range(n)]
    # diffs[i] is the interval between the notes at positions i and i + 1
    diffs = [c5.Int(f"diffs_{i}") for i in range(m)]

    # placed[i][v] is true when pitch-class v is at position i
    placed = [[c5.Bool(f"placed_{i}_{v}") for v in range(n)] for i in range(n)]
    # interval_is[i][k - 1] is true when the interval between positions i and i + 1 is k
    interval_is = [[c5.Bool(f"interval_{i}_{k}") for k in range(1, n)] for i in range(m)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Each note is a pitch-class from 0 to n - 1, and each interval is from 1 to n - 1.
    solver.add([c5.And(xi >= 0, xi <= n - 1) for xi in x])
    solver.add([c5.And(d >= 1, d <= n - 1) for d in diffs])

    # Each position holds exactly one pitch-class, and each pitch-class is at exactly one position.
    for i in range(n):
        solver.add(exactly_one(placed[i]))
    for v in range(n):
        solver.add(exactly_one([placed[i][v] for i in range(n)]))

    # The series x gives the pitch-class at each position.
    for i in range(n):
        for v in range(n):
            solver.add(c5.Implies(placed[i][v], x[i] == v))
            solver.add(c5.Implies(x[i] == v, placed[i][v]))

    # Each pair of neighbouring notes has exactly one interval, and diffs[i] is that interval.
    for i in range(m):
        solver.add(exactly_one(interval_is[i]))
        for k in range(1, n):
            solver.add(c5.Implies(interval_is[i][k - 1], diffs[i] == k))
            solver.add(c5.Implies(diffs[i] == k, interval_is[i][k - 1]))

    # The interval between two neighbouring notes is the distance between their pitch-classes.
    for i in range(m):
        for a in range(n):
            for b in range(n):
                if a != b:
                    solver.add(c5.Implies(
                        c5.And(placed[i][a], placed[i + 1][b]), interval_is[i][abs(a - b) - 1]))

    # The same relation the other way: after a note a, an interval k leads to a + k or a - k.
    for i in range(m):
        for k in range(1, n):
            for a in range(n):
                nexts = [placed[i + 1][b] for b in (a + k, a - k) if 0 <= b < n]
                lhs = c5.And(interval_is[i][k - 1], placed[i][a])
                if not nexts:
                    solver.add(c5.Not(lhs))
                else:
                    solver.add(c5.Implies(lhs, nexts[0] if len(nexts) == 1 else c5.Or(nexts)))

    # The intervals 1 to n - 1 each occur between exactly one pair of neighbouring notes.
    for k in range(1, n):
        solver.add(exactly_one([interval_is[i][k - 1] for i in range(m)]))

    return solver, {"x": x, "diffs": diffs}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
