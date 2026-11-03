# csplib_056_sonet: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_056_sonet.py csplib_056_sonet.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Install n nodes on r rings. Each node on a ring takes one add-drop multiplexer
    (ADM). Nodes that have traffic between them must share a ring, no ring holds more
    nodes than its capacity, and the total number of ADMs is as small as possible."""
    n = instance["n"]                     # the number of nodes
    r = instance["r"]                     # the number of rings
    demand = instance["demand"]           # demand[i][j]: the traffic between nodes i and j
    capacity = instance["capacity_nodes"]  # capacity[k]: the most nodes ring k can host

    # on_ring[k][i] is true when node i is installed on ring k
    on_ring = [[Bool(f"on_ring_{k}_{i}") for i in range(n)] for k in range(r)]

    # Ring k holds no more nodes than its capacity.
    constraints = [sum(on_ring[k]) <= capacity[k] for k in range(r)]

    # Nodes i and j share a ring when there is traffic between them in either direction.
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] == 0 and demand[j][i] == 0:
                continue
            # shared[k] can only be true when nodes i and j are both on ring k
            shared = []
            for k in range(r):
                shared_k = Bool(f"shared_{k}_{i}_{j}")
                constraints.append(If(shared_k, on_ring[k][i]))
                constraints.append(If(shared_k, on_ring[k][j]))
                shared.append(shared_k)
            constraints.append(sum(shared) >= 1)

    # Each node on a ring takes one ADM. The total is the number of ADMs.
    total_adms = sum(on_ring[k][i] for k in range(r) for i in range(n))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_adms, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"ring_config": on_ring, "total_adms": total_adms}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
