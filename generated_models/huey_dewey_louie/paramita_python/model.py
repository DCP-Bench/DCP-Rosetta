# huey_dewey_louie: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python huey_dewey_louie.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Iff, add_to_container, to_cnf


def create_model(instance):
    """Huey, Dewey and Louie are cub scouts questioned by their uncle, so each of their
    statements is true. Who is guilty?"""
    huey = Bool("huey")    # Huey is guilty
    dewey = Bool("dewey")  # Dewey is guilty
    louie = Bool("louie")  # Louie is guilty

    subject_to = []  # the three statements, each taken as true

    # Huey: Dewey and Louie share the guilt equally: if one is guilty, so is the other.
    subject_to.append(Iff(dewey, louie))
    # Dewey: if Huey is guilty, then so am I.
    subject_to.append(If(huey, dewey))
    # Louie: Dewey and I are not both guilty.
    subject_to.append(~(dewey & louie))

    outputs = {"dewey": dewey, "huey": huey, "louie": louie}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

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
