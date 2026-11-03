# csplib_019_magic_squares_and_sequences: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

import cvc5.pythonic as c5


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1}
    between 0 and n-1 such that, for every i, the number i occurs exactly x_i times
    in the sequence."""
    n = instance["n"]  # the length of the sequence

    # x[i] is the number at position i, so it is also how often the number i occurs
    x = [c5.Int(f"x_{i}") for i in range(n)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Each number in the sequence is between 0 and n-1.
    solver.add([c5.And(xi >= 0, xi <= n - 1) for xi in x])

    # The number i occurs exactly x[i] times: count the positions that hold i.
    for i in range(n):
        solver.add(x[i] == c5.Sum([c5.If(x[j] == i, 1, 0) for j in range(n)]))

    # The counts of all numbers add up to the length of the sequence.
    solver.add(c5.Sum(x) == n)

    # The numbers in the sequence add up to n: each number i counts i for each of its x[i]
    # occurrences.
    solver.add(c5.Sum([i * x[i] for i in range(n)]) == n)

    return solver, {"x": x}


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
