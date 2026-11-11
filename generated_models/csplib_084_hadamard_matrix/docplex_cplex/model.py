# csplib_084_hadamard_matrix: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from docplex.mp.model import Model


def create_model(instance):
    """Hadamard matrix by Legendre pairs (two-circulant construction): find two sequences a and b of
    odd length l with entries -1 or 1, each adding up to 1, such that for every shift s in
    1..(l-1)/2 the periodic autocorrelations add up to -2: PAF(a, s) + PAF(b, s) = -2, where
    PAF(a, s) is the sum over i of a[i] * a[(i + s) mod l]."""
    l = instance["l"]  # length of the sequences (odd)
    m = (l - 1) // 2   # the shifts 1..m are constrained

    model = Model("hadamard_matrix")
    idx = range(l)  # the positions of a sequence
    # Each sequence adds up to 1, so (l + 1) / 2 of its entries are 1 and the rest -1.
    ones = (l + 1) // 2

    def sequence(name):
        # up[i] is 1 when entry i is 1 and 0 when it is -1; the entry is 2 * up[i] - 1.
        up = [model.binary_var(name=f"{name}_up_{i}") for i in idx]
        entries = [2 * up[i] - 1 for i in idx]

        # The entries add up to 1.
        model.add_constraint(model.sum(entries) == 1)

        # both[i, j] (i < j) equals up[i] * up[j], so that a[i] * a[j], which is
        # 4 * up[i] * up[j] - 2 * up[i] - 2 * up[j] + 1, is linear. The product is pinned down
        # without one constraint per pair from below: both[i, j] is at most up[i] and up[j],
        # and for each i the products with all other entries add up to up[i] * (ones - 1),
        # because exactly ones - 1 other entries are 1 when entry i is. When up[i] = 0 this
        # forces every product to 0; when up[i] = 1 it forces both[i, j] = up[j].
        both = {}
        for i in idx:
            for j in range(i + 1, l):
                both[i, j] = model.continuous_var(0, 1, name=f"{name}_both_{i}_{j}")
                model.add_constraint(both[i, j] <= up[i])
                model.add_constraint(both[i, j] <= up[j])
        for i in idx:
            model.add_constraint(
                model.sum(both[min(i, j), max(i, j)] for j in idx if j != i) == (ones - 1) * up[i])

        def product(i, j):
            i, j = min(i, j), max(i, j)
            return 4 * both[i, j] - 2 * up[i] - 2 * up[j] + 1

        def paf(s):
            return model.sum(product(i, (i + s) % l) for i in idx)

        return entries, paf

    a, paf_a = sequence("a")
    b, paf_b = sequence("b")

    # For every shift s in 1..m, PAF(a, s) + PAF(b, s) = -2.
    for s in range(1, m + 1):
        model.add_constraint(paf_a(s) + paf_b(s) == -2)

    return model, {"a": a, "b": b}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
