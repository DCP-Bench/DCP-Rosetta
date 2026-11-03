# csplib_050_diamond_free: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from itertools import combinations

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def number_up_to(name, k_max):
    """Bools for a number from 0 to k_max: ge[k] is true when the number is at least k + 1."""
    ge = [Bool(f"{name}_ge_{k}") for k in range(1, k_max + 1)]
    # A number that is at least k + 1 is also at least k.
    cons = [If(ge[k], ge[k - 1]) for k in range(1, len(ge))]
    return ge, cons


def create_model(instance):
    """Find a simple undirected graph on N vertices with no diamond (four vertices with five or
    more edges between them), where every vertex has a degree that is a positive multiple of 3,
    the degrees are listed from largest to smallest, and the sum of the degrees is a multiple of 12."""
    n = instance["N"]  # the number of vertices
    vertices = range(n)

    # matrix[u][v] is true when vertices u and v are joined by an edge. The graph has no loops
    # and an edge joins both ends, so the diagonal is empty and the matrix is symmetric.
    matrix = [[False] * n for _ in vertices]
    for u, v in combinations(vertices, 2):
        matrix[u][v] = matrix[v][u] = Bool(f"edge_{u}_{v}")

    # deg[v] is the number of edges at vertex v.
    deg = [sum(matrix[v][u] for u in vertices if u != v) for v in vertices]

    constraints = []

    # Each degree is a positive multiple of 3: deg[v] = 3 * q_v for a number q_v of at least 1.
    for v in vertices:
        q_ge, q_cons = number_up_to(f"q_{v}", (n - 1) // 3)
        constraints += q_cons
        constraints.append(deg[v] == 3 * sum(q_ge) if q_ge else deg[v] == 0)
        if q_ge:
            constraints.append(q_ge[0])

    # The degrees are listed from largest to smallest.
    for v in range(n - 1):
        constraints.append(deg[v] >= deg[v + 1])

    # The sum of the degrees, with each edge counted at both ends, is 12 * t for a number t.
    total = sum(deg)
    t_ge, t_cons = number_up_to("t", n * (n - 1) // 12)
    constraints += t_cons
    constraints.append(total == 12 * sum(t_ge) if t_ge else total == 0)

    # Any four vertices have at most four edges between them.
    for quad in combinations(vertices, 4):
        constraints.append(sum(matrix[a][b] for a, b in combinations(quad, 2)) <= 4)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
