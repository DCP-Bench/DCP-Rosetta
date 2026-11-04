# crew: a Paramita (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python crew.py crew.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a certain number of cabin
    crew, and they have to speak certain languages. Every cabin crew member has two
    flights off after an attended flight."""
    # attributes[p]: whether person p is a steward, a hostess, and speaks French, Spanish
    # and German (1 if so, 0 if not)
    attributes = instance["attributes"]
    # required_crew[f]: the number of crew flight f needs, then the minimum number of
    # stewards, hostesses and speakers of French, Spanish and German among them
    required_crew = instance["required_crew"]
    n_people = len(attributes)
    n_flights = len(required_crew)

    # crew[f][p] is true when person p works on flight f
    crew = [[Bool(f"crew_{f}_{p}") for p in range(n_people)] for f in range(n_flights)]

    constraints = []  # the constraints of the roster, collected below
    for f in range(n_flights):
        # Flight f has exactly as many crew members as it needs.
        constraints.append(sum(crew[f]) == required_crew[f][0])
        # Flight f has at least the required number of people with each attribute.
        for a in range(5):
            constraints.append(
                sum(crew[f][p] for p in range(n_people) if attributes[p][a] == 1) >= required_crew[f][a + 1]
            )

    # A person who works on a flight has the next two flights off, so works on at most one
    # of any three consecutive flights.
    for p in range(n_people):
        for f in range(n_flights - 2):
            constraints.append(crew[f][p] + crew[f + 1][p] + crew[f + 2][p] <= 1)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"crew": crew}


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
