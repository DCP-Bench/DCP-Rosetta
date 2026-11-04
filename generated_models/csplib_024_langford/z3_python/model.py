# csplib_024_langford: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_024_langford.py csplib_024_langford.json

import z3


def create_model(instance):
    """Arrange two copies of each number from 1 to k into one sequence of 2k numbers, so that the
    two 1's are one number apart, the two 2's two numbers apart, ..., and the two k's k numbers
    apart."""
    k = instance["k"]  # the largest number; each of 1 to k appears twice in the sequence
    size = 2 * k       # the length of the sequence

    # sol[j] is the number at place j of the sequence
    sol = [z3.Int(f"sol_{j}") for j in range(size)]

    # position[j] is the place of copy j: the first copy of number j + 1 for j < k, then the
    # second copies in the same order
    position = [z3.Int(f"position_{j}") for j in range(size)]

    solver = z3.Solver()

    # Each number is from 1 to k.
    solver.add([z3.And(value >= 1, value <= k) for value in sol])

    # Each place is from 0 to size - 1.
    solver.add([z3.And(slot >= 0, slot <= size - 1) for slot in position])

    # Every copy has its own place.
    solver.add(z3.Distinct(position))

    # The lookup table holds the sequence, so a place can be read through its position.
    table = z3.Array("sol_table", z3.IntSort(), z3.IntSort())
    solver.add([z3.Select(table, j) == sol[j] for j in range(size)])

    for value in range(1, k + 1):
        # The places of the two copies of value
        first, second = position[value - 1], position[k + value - 1]
        # The second copy is value + 1 places after the first, so value numbers lie between them.
        solver.add(second == first + value + 1)
        # Both places hold value.
        solver.add(z3.Select(table, first) == value)
        solver.add(z3.Select(table, second) == value)

    return solver, {"sol": sol}


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
