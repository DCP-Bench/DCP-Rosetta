# appointment_scheduling: a Paramita (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python appointment_scheduling.py appointment_scheduling.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Schedule the people into interview slots from their free-busy schedules: each
    person gets one slot in which they are free, and each slot gets one person."""
    free = instance["m"]  # free[i][j] is 1 when person i is free in slot j
    n_people = len(free)  # the number of people, which is also the number of slots

    # assigned[i][j] is true when person i is interviewed in slot j
    assigned = [[Bool(f"assigned_{i}_{j}") for j in range(n_people)] for i in range(n_people)]

    constraints = []  # the rules the schedule must satisfy
    # Each person is interviewed in exactly one slot.
    for i in range(n_people):
        constraints.append(sum(assigned[i]) == 1)
    # Each slot is used for exactly one person.
    for j in range(n_people):
        constraints.append(sum(assigned[i][j] for i in range(n_people)) == 1)
    # A person is interviewed only in a slot in which they are free.
    for i in range(n_people):
        for j in range(n_people):
            if free[i][j] == 0:
                constraints.append(~assigned[i][j])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": assigned}


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
