# csplib_019_magic_squares_and_sequences: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

from exact import Exact


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1}
    between 0 and n-1 such that, for every i, the number i occurs exactly x_i times
    in the sequence."""
    n_positions = instance["n"]  # the length of the sequence; every entry lies in 0..n-1

    solver = Exact()

    # Exact identifies its variables by name.
    # x[j] is the entry at position j. It is also how often the number j occurs.
    x = [f"x_{j}" for j in range(n_positions)]
    # is_value[j][i] is 1 when the entry at position j is i, and 0 when not
    is_value = [[f"x_{j}_is_{i}" for i in range(n_positions)] for j in range(n_positions)]
    for j in range(n_positions):
        solver.addVariable(x[j], 0, n_positions - 1)
        for name in is_value[j]:
            solver.addVariable(name, 0, 1)
        # Each position holds exactly one number.
        solver.addConstraint([(1, name) for name in is_value[j]], True, 1, True, 1)
        # The entry at position j is the number flagged for that position.
        solver.addConstraint([(i, is_value[j][i]) for i in range(1, n_positions)] + [(-1, x[j])],
                             True, 0, True, 0)

    # The number i occurs exactly x[i] times in the sequence.
    for i in range(n_positions):
        solver.addConstraint([(1, is_value[j][i]) for j in range(n_positions)] + [(-1, x[i])],
                             True, 0, True, 0)

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
