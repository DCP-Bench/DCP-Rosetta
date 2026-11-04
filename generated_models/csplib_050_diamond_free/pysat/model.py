# csplib_050_diamond_free: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def create_model(instance):
    """Find a simple undirected graph on N vertices that has no isolated vertex, where every
    degree is a multiple of 3 and the sum of the degrees is a multiple of 12, and that is
    diamond-free: no four vertices span five or more edges."""
    n_vertices = instance["N"]  # the number of vertices

    pool = IDPool()
    cnf = CNF()

    def one_hot(key, count):
        """Variables for the values 1 to count, of which exactly one is true."""
        choice = [pool.id((key, v)) for v in range(1, count + 1)]
        cnf.extend(CardEnc.equals(lits=choice, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
        return choice

    # matrix[i][j] is true when vertices i and j are joined by an edge. The graph is undirected,
    # so matrix[j][i] is the same variable as matrix[i][j].
    matrix = [[None] * n_vertices for _ in range(n_vertices)]
    for i, j in combinations(range(n_vertices), 2):
        matrix[i][j] = matrix[j][i] = pool.id(("edge", i, j))
    # No vertex is joined to itself.
    for i in range(n_vertices):
        matrix[i][i] = False

    # The degree of vertex i is 3 * k_i for some k_i from 1 to max_multiple, so every degree is a
    # positive multiple of 3. A degree is at most n_vertices - 1.
    max_multiple = (n_vertices - 1) // 3
    for i in range(n_vertices):
        neighbours = [matrix[i][j] for j in range(n_vertices) if j != i]
        multiple = one_hot(("degree_multiple", i), max_multiple)
        cnf.extend(PBEnc.equals(lits=neighbours + multiple,
                                weights=[1] * len(neighbours) + [-3 * v for v in range(1, max_multiple + 1)],
                                bound=0, vpool=pool).clauses)

    # The degrees add up to twice the number of edges. The sum is a multiple of 12, so the number
    # of edges is 6 * t for some t from 1 to max_edge_multiple.
    edges = [matrix[i][j] for i, j in combinations(range(n_vertices), 2)]
    max_edge_multiple = len(edges) // 6
    edge_multiple = one_hot("edge_multiple", max_edge_multiple)
    cnf.extend(PBEnc.equals(lits=edges + edge_multiple,
                            weights=[1] * len(edges) + [-6 * v for v in range(1, max_edge_multiple + 1)],
                            bound=0, vpool=pool).clauses)

    # Diamond-free: any four vertices span at most four of their six possible edges.
    for a, b, c, d in combinations(range(n_vertices), 4):
        group = [matrix[a][b], matrix[a][c], matrix[a][d],
                 matrix[b][c], matrix[b][d], matrix[c][d]]
        cnf.extend(CardEnc.atmost(lits=group, bound=4, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
