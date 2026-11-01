# csplib_084_hadamard_matrix: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from pychoco.model import Model


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each
    sum to 1 and whose periodic autocorrelations add up to -2 at every shift
    s = 1, ..., (l-1)/2 (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]  # length of each sequence, an odd positive integer
    m = (l - 1) // 2   # number of shifts that are constrained

    model = Model()

    # plus_a[i] is 1 when entry i of a is +1, and 0 when it is -1. Likewise for b.
    plus_a = [model.boolvar(name=f"plus_a_{i}") for i in range(l)]
    plus_b = [model.boolvar(name=f"plus_b_{i}") for i in range(l)]

    # a[i] and b[i] are the entries of the two sequences, each -1 or +1.
    a = [model.intvar([-1, 1], name=f"a_{i}") for i in range(l)]
    b = [model.intvar([-1, 1], name=f"b_{i}") for i in range(l)]

    # Each entry is +1 when its plus_ value is 1 and -1 otherwise.
    for entries, pluses in ((a, plus_a), (b, plus_b)):
        for entry, plus in zip(entries, pluses):
            model.scalar([plus, entry], [2, -1], "=", 1).post()

    # Each sequence sums to 1.
    model.sum(a, "=", 1).post()
    model.sum(b, "=", 1).post()

    # At each shift s, the periodic autocorrelations of a and b add up to -2. A pair of
    # entries at distance s (mod l) multiplies to +1 when the entries agree and -1 when
    # they differ, so exactly l + 1 of the 2l pairs must differ.
    for s in range(1, m + 1):
        differing = []  # the pairs at shift s whose entries differ
        for pluses in (plus_a, plus_b):
            for i in range(l):
                differing.append(model.arithm(pluses[i], "!=", pluses[(i + s) % l]).reify())
        model.sum(differing, "=", l + 1).post()

    return model, {"a": a, "b": b}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
