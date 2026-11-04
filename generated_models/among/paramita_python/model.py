# among: a Paramita (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python among.py among.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Exactly m of the values in x take one of the values in v. Every value in x
    is at least 0 and at most 7."""
    n_values = instance["n"]  # the number of values in x
    m = instance["m"]         # how many values in x must take a value from v
    v = instance["v"]         # the values that are counted

    # The values an entry of x may take.
    domain = range(8)

    # is_value[i][d] is true when entry i of x takes the value d.
    is_value = [{d: Bool(f"is_value_{i}_{d}") for d in domain} for i in range(n_values)]

    # The constraints of the problem.
    constraints = []

    # Each entry of x takes exactly one value from the domain.
    constraints += [sum(is_value[i].values()) == 1 for i in range(n_values)]

    # in_v[i] is true when entry i of x takes a value from v.
    in_v = [sum(is_value[i][d] for d in v) for i in range(n_values)]
    # Exactly m entries of x take a value from v.
    constraints.append(sum(in_v) == m)

    # The entries of x, each as its value.
    x = [sum(d * is_value[i][d] for d in domain) for i in range(n_values)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": x}


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
