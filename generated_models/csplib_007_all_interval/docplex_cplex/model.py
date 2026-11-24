# csplib_007_all_interval: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

from docplex.mp.model import Model


def create_model(instance):
    """All-interval series: order 0..n-1 so that the distances between neighbours are 1..n-1, each once."""
    n = instance["n"]  # the number of pitch classes: the series has n notes
    places = range(n)  # the places of the series
    gaps = range(n - 1)  # the gaps between neighbouring places
    pitches = range(n)  # the pitch classes 0 .. n - 1
    intervals = range(1, n)  # the intervals 1 .. n - 1

    model = Model("all_interval")

    # note[i, v] is 1 when place i holds pitch class v, and 0 when not
    note = model.binary_var_matrix(places, pitches, name="note")
    # Each place holds one pitch class and each pitch class occurs once: the series is a
    # permutation of 0..n-1.
    model.add_constraints(model.sum(note[i, v] for v in pitches) == 1 for i in places)
    model.add_constraints(model.sum(note[i, v] for i in places) == 1 for v in pitches)
    # x[i] is the pitch class at place i
    x = [model.sum(v * note[i, v] for v in pitches) for i in places]

    # interval[i, d] is 1 when the i-th interval is d, and 0 when not
    interval = model.binary_var_matrix(gaps, intervals, name="interval")
    # Each gap has one interval and each interval occurs once: the intervals are a
    # permutation of 1..n-1.
    model.add_constraints(model.sum(interval[i, d] for d in intervals) == 1 for i in gaps)
    model.add_constraints(model.sum(interval[i, d] for i in gaps) == 1 for d in intervals)
    # diffs[i] is the interval between the notes at places i and i + 1
    diffs = [model.sum(d * interval[i, d] for d in intervals) for i in gaps]

    # Each interval is the distance between neighbouring notes.
    for i in gaps:
        model.add_constraint(diffs[i] == model.abs(x[i + 1] - x[i]), ctname=f"distance_{i}")

    return model, {"x": x, "diffs": diffs}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
