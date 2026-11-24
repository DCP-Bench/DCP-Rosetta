# csplib_028_bibd: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_028_bibd.py csplib_028_bibd.json

from docplex.mp.model import Model


def create_model(instance):
    """Balanced incomplete block design (BIBD): a v-by-b 0/1 incidence matrix of objects and blocks
    in which every object occurs in r blocks, every block holds k objects, and every pair of
    distinct objects occurs together in exactly l blocks."""
    v = instance["v"]  # number of distinct objects (rows)
    b = instance["b"]  # number of blocks (columns)
    r = instance["r"]  # number of blocks each object occurs in
    k = instance["k"]  # number of objects each block contains
    l = instance["l"]  # number of blocks each pair of distinct objects shares

    model = Model("bibd")
    # The pair rule is a quadratic constraint over binaries, which is not convex. CPLEX refuses
    # such a constraint unless it is told to search for a global optimum.
    model.parameters.optimalitytarget = 3

    # matrix[i][j] is 1 when object i occurs in block j.
    matrix = [[model.binary_var(name=f"matrix_{i}_{j}") for j in range(b)] for i in range(v)]

    # Every row adds up to r: each object occurs in r blocks.
    model.add_constraints(model.sum(matrix[i]) == r for i in range(v))

    # Every column adds up to k: each block contains k objects.
    model.add_constraints(model.sum(matrix[i][j] for i in range(v)) == k for j in range(b))

    # The scalar product of every pair of rows adds up to l: each pair of objects shares l
    # blocks. Only the "at most l" side is posted as a quadratic constraint. With every column
    # holding k objects, the scalar products of all pairs of rows add up to b * C(k, 2), a
    # fixed number; when that equals C(v, 2) * l, "at most l" for every pair forces "exactly
    # l". Otherwise the "at least l" side is posted too, so the model stays exact.
    pairs = [(i, h) for i in range(v) for h in range(i + 1, v)]
    at_most_forces_exact = b * k * (k - 1) // 2 == len(pairs) * l
    for i, h in pairs:
        shared = model.sum(matrix[i][j] * matrix[h][j] for j in range(b))
        model.add_constraint(shared <= l)
        if not at_most_forces_exact:
            model.add_constraint(shared >= l)

    return model, {"matrix": matrix}


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
