# csplib_050_diamond_free: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from itertools import combinations
from docplex.mp.model import Model


def create_model(instance):
    """Diamond-free graph: a simple undirected graph on N vertices in which no four vertices have at
    least five edges among them (a diamond), every vertex has a positive degree that is a multiple
    of 3, and the degrees add up to a multiple of 12."""
    n = instance["N"]  # number of vertices
    vertices = range(n)

    model = Model("diamond_free")

    # edge[u, v] is 1 when u and v are adjacent, for u < v. The matrix is symmetric and has
    # no loops, so the lower triangle and the diagonal need no variables of their own.
    edge = {(u, v): model.binary_var(name=f"edge_{u}_{v}") for u, v in combinations(vertices, 2)}

    def adjacent(u, v):
        return edge[(u, v)] if u < v else edge[(v, u)]

    # Every vertex has a positive degree that is a multiple of 3: degree = 3 * groups with
    # groups at least 1. At most n - 1 other vertices can be neighbours.
    degree = []
    for u in vertices:
        groups = model.integer_var(1, (n - 1) // 3, name=f"groups_{u}")
        row_sum = model.sum(adjacent(u, v) for v in vertices if v != u)
        model.add_constraint(row_sum == 3 * groups)
        degree.append(row_sum)

    # The sum of the matrix (the sum of all degrees) is a multiple of 12.
    twelves = model.integer_var(0, n * (n - 1) // 12, name="twelves")
    model.add_constraint(model.sum(degree) == 12 * twelves)

    # No diamond. Four vertices hold at least five edges exactly when one edge lies in two
    # triangles: its two ends plus two more vertices adjacent to both. So it is enough to
    # allow every edge at most one triangle. This takes one row per triple of vertices and
    # one per edge, where "at most four edges among every four vertices" would take one row
    # per quadruple, more than the Community Edition's 1000 rows once n reaches 14.
    # triangle[t] is forced to 1 when all three edges of the triple t are present.
    triangle = {}
    for u, v, w in combinations(vertices, 3):
        triangle[(u, v, w)] = model.binary_var(name=f"triangle_{u}_{v}_{w}")
        model.add_constraint(
            triangle[(u, v, w)] >= edge[(u, v)] + edge[(u, w)] + edge[(v, w)] - 2)
    for u, v in combinations(vertices, 2):
        model.add_constraint(
            model.sum(triangle[tuple(sorted((u, v, w)))] for w in vertices if w not in (u, v)) <= 1)

    # The declared output: the adjacency matrix, with 0 on the diagonal (no loops).
    matrix = [[adjacent(u, v) if u != v else 0 for v in vertices] for u in vertices]
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
