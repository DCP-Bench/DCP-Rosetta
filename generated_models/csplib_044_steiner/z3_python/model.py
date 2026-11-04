# csplib_044_steiner: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

import z3


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements out of 1 to n such that any two
    triples have at most one element in common (n is 1 or 3 modulo 6)."""
    n = instance["n"]              # the number of elements; n modulo 6 is 1 or 3
    n_triples = n * (n - 1) // 6   # the number of triples in the system

    # triples[i][j] is true when element j is in triple i
    triples = [[z3.Bool(f"triples_{i}_{j}") for j in range(n)] for i in range(n_triples)]

    solver = z3.Solver()

    # Each triple has exactly three elements.
    solver.add([z3.PbEq([(x, 1) for x in triple], 3) for triple in triples])

    # Any two elements lie together in exactly one triple. The triples hold three pairs each,
    # which adds up to every pair of elements, so no pair can lie together in two triples.
    for a in range(n):
        for b in range(a + 1, n):
            # Each triple that contains both a and b counts once.
            together = [(z3.And(triple[a], triple[b]), 1) for triple in triples]
            solver.add(z3.PbEq(together, 1))

    return solver, {"sets": triples}


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
