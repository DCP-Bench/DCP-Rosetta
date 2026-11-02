# clock_triplets: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install cvc5 numpy`) with:
#   python clock_triplets.py

import cvc5.pythonic as c5


def create_model(instance):
    """Rearrange the numbers on the face of a clock (1 to 12) so that no triplet of
    adjacent numbers has a sum higher than 21, the smallest value the highest
    triplet sum can have."""
    n_numbers = 12  # how many numbers are on the clock face
    max_sum = 21    # the largest allowed sum of three adjacent numbers
    numbers = range(1, n_numbers + 1)  # the numbers on the clock face

    # at[i, v] is true when the number v is at position i of the clock face, counting round the face
    at = {(i, v): c5.Bool(f"at_{i}_{v}") for i in range(n_numbers) for v in numbers}

    solver = c5.Solver()

    # Each position holds exactly one number.
    for i in range(n_numbers):
        solver.add(c5.Or([at[i, v] for v in numbers]))
        for v in numbers:
            for w in numbers:
                if v < w:
                    solver.add(c5.Not(c5.And(at[i, v], at[i, w])))

    # Each number appears at exactly one position.
    for v in numbers:
        solver.add(c5.Or([at[i, v] for i in range(n_numbers)]))
        for i in range(n_numbers):
            for j in range(i + 1, n_numbers):
                solver.add(c5.Not(c5.And(at[i, v], at[j, v])))

    # No three adjacent positions, wrapping round the face, hold numbers that sum to more
    # than max_sum.
    for i in range(n_numbers):
        p, q, r = i, (i + 1) % n_numbers, (i + 2) % n_numbers
        for a in numbers:
            for c in numbers:
                for d in numbers:
                    if a + c + d > max_sum:
                        solver.add(c5.Not(c5.And(at[p, a], at[q, c], at[r, d])))

    # x[i] is the number at position i of the clock face.
    x = [c5.Sum([c5.If(at[i, v], v, 0) for v in numbers]) for i in range(n_numbers)]
    return solver, {"x": x}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
