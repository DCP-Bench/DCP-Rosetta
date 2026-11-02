# csplib_005_autocorrelation: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

import z3


def create_model(instance):
    """Choose a sequence of n values, each -1 or +1, that minimises the sum of the squared
    periodic autocorrelations C_k = sum_i S_i * S_((i+k) mod n), for k = 1 to n-1."""
    n = instance["n"]  # the length of the sequence

    # sequence[i] is the value S_i
    sequence = [z3.Int(f"sequence_{i}") for i in range(n)]

    solver = z3.Optimize()

    # Each value is -1 or +1.
    solver.add([z3.Or(bit == -1, bit == 1) for bit in sequence])

    # C_k pairs each value with the value k places further on, cyclically. A pair of equal
    # values adds +1 to C_k and a pair of unequal values adds -1.
    # C_k is a sum of n such terms, so it lies between -n and n and has the parity of n.
    # C_k is equal to C_(n-k), so shifts 1 to n // 2 are enough. The middle shift of an even
    # n is its own mirror and counts once; every other shift counts twice.
    # weighted_squares: the squares of C_1 to C_(n // 2), each with its count.
    weighted_squares = []
    for k in range(1, n // 2 + 1):
        correlation = z3.Int(f"correlation_{k}")  # C_k
        square = z3.Int(f"square_{k}")  # the square of C_k
        solver.add(
            correlation == z3.Sum([z3.If(sequence[i] == sequence[(i + k) % n], 1, -1)
                           for i in range(n)]))
        solver.add(
            z3.Or([z3.And(correlation == v, square == v * v)
                   for v in range(-n, n + 1) if (v - n) % 2 == 0]))
        weight = 1 if 2 * k == n else 2
        weighted_squares.append(weight * square)

    # E, the sum of the squared autocorrelations over all shifts 1 to n - 1, is minimised.
    energy = z3.Sum(weighted_squares)
    solver.minimize(energy)

    return solver, {"sequence": sequence}


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
