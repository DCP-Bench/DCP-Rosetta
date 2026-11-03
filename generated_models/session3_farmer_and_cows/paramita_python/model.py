# session3_farmer_and_cows: a Paramita (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and each cow gives
    as much milk as its number. He gives each of his sons a set number of cows,
    so that every son gets the same total quantity of milk. Decide which son
    gets each cow."""
    num_cows = instance["num_cows"]          # the number of cows
    num_sons = instance["num_sons"]          # the number of sons
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s is given

    # gets[i][s] is true when son s is given cow i + 1
    gets = [[Bool(f"cow_{i}_son_{s}") for s in range(num_sons)] for i in range(num_cows)]

    # milk[s]: the total milk of son s, the numbers of his cows added up
    milk = [sum((i + 1) * gets[i][s] for i in range(num_cows)) for s in range(num_sons)]

    # the conditions every distribution must meet
    constraints = []
    # Each cow goes to exactly one son.
    constraints += [sum(gets[i]) == 1 for i in range(num_cows)]
    # Each son gets the number of cows set for him.
    constraints += [sum(gets[i][s] for i in range(num_cows)) == cows_per_son[s] for s in range(num_sons)]
    # Every son gets the same total milk as the first son.
    constraints += [milk[s] == milk[0] for s in range(1, num_sons)]

    # The son who is given each cow.
    cow_assignments = [sum(s * gets[i][s] for s in range(num_sons)) for i in range(num_cows)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"cow_assignments": cow_assignments}


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
