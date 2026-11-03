# csplib_019_magic_squares_and_sequences: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

import z3


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1}
    between 0 and n-1 such that, for every i, the number i occurs exactly x_i times
    in the sequence."""
    n_positions = instance["n"]  # the length of the sequence

    # x[i] is the number at position i
    x = [z3.Int(f"x_{i}") for i in range(n_positions)]

    solver = z3.Solver()

    # Every number in the sequence is between 0 and n-1.
    solver.add([z3.And(value >= 0, value <= n_positions - 1) for value in x])

    # The number i occurs exactly x[i] times in the sequence.
    for i in range(n_positions):
        solver.add(x[i] == z3.Sum([z3.If(value == i, 1, 0) for value in x]))

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
