# finding_celebrities: a Paramita (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python finding_celebrities.py finding_celebrities.json

from paramita.containers import CnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, Iff, Or, add_to_container, to_cnf


def create_model(instance):
    """At a party, a celebrity is a person whom everybody knows but who only
    knows other celebrities. Find the celebrities; at least one is present."""
    graph = instance["graph"]  # graph[j][i] is 1 when person j knows person i
    n_people = len(graph)      # the number of people at the party

    # celebrities[i] is true when person i is a celebrity
    celebrities = [Bool(f"celebrity_{i}") for i in range(n_people)]
    constraints = []

    for i in range(n_people):
        # Somebody at the party does not know person i, so person i is no celebrity.
        if not all(graph[j][i] == 1 for j in range(n_people)):
            constraints.append(~celebrities[i])
            continue

        # The people that person i knows, other than i.
        others = [j for j in range(n_people) if j != i and graph[i][j] == 1]
        # A celebrity knows only celebrities, so person i is a celebrity exactly when
        # everyone that person i knows is one.
        if not others:
            constraints.append(celebrities[i])
        elif len(others) == 1:
            constraints.append(Iff(celebrities[i], celebrities[others[0]]))
        else:
            constraints.append(Iff(celebrities[i], And([celebrities[j] for j in others])))

    # At least one celebrity is at the party.
    constraints.append(Or(celebrities))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"celebrities": celebrities}


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
