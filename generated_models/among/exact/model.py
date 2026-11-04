# among: an Exact (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python among.py among.json

from exact import Exact


def create_model(instance):
    """Find an array x of n values, each from 0 to 7, such that exactly m of its
    entries take a value listed in v."""
    n_entries = instance["n"]  # the length of x
    n_matches = instance["m"]  # how many entries of x take a value listed in v
    v = instance["v"]          # the values that count
    max_value = 7              # the largest value an entry of x can take

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is entry i of the array.
    x = [f"x_{i}" for i in range(n_entries)]
    # is_value[i][a] is 1 when entry i takes the value a, and 0 when not.
    is_value = [[f"x_{i}_is_{a}" for a in range(max_value + 1)] for i in range(n_entries)]
    for i in range(n_entries):
        solver.addVariable(x[i], 0, max_value)
        for name in is_value[i]:
            solver.addVariable(name, 0, 1)

    # Each entry takes exactly one value, and that value is the entry.
    for i in range(n_entries):
        solver.addConstraint([(1, name) for name in is_value[i]], True, 1, True, 1)
        solver.addConstraint([(a, is_value[i][a]) for a in range(1, max_value + 1)] + [(-1, x[i])],
                             True, 0, True, 0)

    # Exactly n_matches entries take a value listed in v. A value listed twice in v counts twice.
    hits = [(v.count(a), is_value[i][a]) for i in range(n_entries) for a in range(max_value + 1) if v.count(a)]
    solver.addConstraint(hits, True, n_matches, True, n_matches)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
