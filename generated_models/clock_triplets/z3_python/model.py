# clock_triplets: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install z3-solver numpy`) with:
#   python clock_triplets.py

import z3


def create_model(instance):
    """Rearrange the numbers on the face of a clock (1 to 12) so that no triplet of
    adjacent numbers has a sum higher than 21, the smallest value the highest
    triplet sum can have."""
    n = 12           # numbers on the clock face
    max_triplet = 21  # largest allowed sum of three adjacent numbers

    # x[i] is the number at position i of the clock face
    x = z3.IntVector("x", n)

    solver = z3.Solver()

    # Each position holds a number from 1 to 12.
    solver.add([z3.And(v >= 1, v <= n) for v in x])

    # Each number from 1 to 12 appears once on the clock.
    solver.add(z3.Distinct(x))

    # Every three adjacent numbers, wrapping around the face, sum to at most 21.
    for i in range(n):
        solver.add(x[i] + x[(i - 1) % n] + x[(i - 2) % n] <= max_triplet)

    return solver, {"x": x}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
