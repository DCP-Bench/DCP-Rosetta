# contracting_costs: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python contracting_costs.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """A contractor has to pay six pairs of tradesmen a known sum for each pair.
    What does each man charge for his services?"""
    # The six tradesmen, in the order of the statement.
    names = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]

    # charge_bits[name][k] is true when that tradesman's charge includes 2**k dollars.
    # Thirteen places reach 8191, more than the largest bill of 5300.
    charge_bits = {name: [Bool(f"{name}_bit_{k}") for k in range(13)] for name in names}

    # charge[name] is what that tradesman charges, in dollars.
    charge = {name: sum(2**k * b for k, b in enumerate(charge_bits[name])) for name in names}

    constraints = [
        # $1,100 to the paper hanger and the painter.
        charge["paper_hanger"] + charge["painter"] == 1100,
        # $1,700 to the painter and plumber.
        charge["painter"] + charge["plumber"] == 1700,
        # $1,100 to the plumber and electrician.
        charge["plumber"] + charge["electrician"] == 1100,
        # $3,300 to the electrician and carpenter.
        charge["electrician"] + charge["carpenter"] == 3300,
        # $5,300 to the carpenter and mason.
        charge["carpenter"] + charge["mason"] == 5300,
        # $3,200 to the mason and painter.
        charge["mason"] + charge["painter"] == 3200,
    ]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), charge


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
