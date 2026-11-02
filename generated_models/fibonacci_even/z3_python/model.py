# fibonacci_even: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install z3-solver numpy`) with:
#   python fibonacci_even.py

import z3


def create_model(instance):
    """Each new term of the Fibonacci sequence is the sum of the two before it, starting from
    1 and 2. Find the sum of the even-valued terms that do not exceed four million."""
    limit = 4000000  # four million, the largest term that counts
    n = 35           # terms f[0] to f[n] are generated; f[35] = 9227465 is already above the limit
    max_term = 10000000  # bound on every generated term, above f[35]

    # f[i] is the i-th term of the Fibonacci sequence 0, 1, 1, 2, 3, 5, ...; the puzzle's terms
    # 1, 2, 3, 5, ... are f[2], f[3], ...
    f = [z3.Int(f"f_{i}") for i in range(n + 1)]
    # counted[i] is true when term i is even and does not exceed four million
    counted = [z3.Bool(f"counted_{i}") for i in range(n + 1)]
    # res is the sum of the counted terms
    res = z3.Int("res")

    solver = z3.Solver()

    # Every term lies between zero and the bound.
    solver.add([f[i] >= 0 for i in range(n + 1)])
    solver.add([f[i] <= max_term for i in range(n + 1)])

    # The sequence starts 0, 1, 1 and each later term is the sum of the two before it.
    solver.add(f[0] == 0, f[1] == 1, f[2] == 1)
    solver.add([f[i] == f[i - 1] + f[i - 2] for i in range(3, n + 1)])

    # f[0] is not a term of the puzzle, so it is never counted.
    solver.add(z3.Not(counted[0]))

    # A term is counted when it is even and does not exceed four million.
    solver.add([counted[i] == z3.And(f[i] % 2 == 0, f[i] <= limit) for i in range(1, n + 1)])

    # The answer is the sum of the counted terms.
    solver.add(res == z3.Sum([z3.If(counted[i], f[i], 0) for i in range(1, n + 1)]))

    return solver, {"res": res}


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
