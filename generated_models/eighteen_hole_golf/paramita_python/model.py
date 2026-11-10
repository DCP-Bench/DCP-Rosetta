# eighteen_hole_golf: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python eighteen_hole_golf.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """A golf course has 18 holes, each of length 3, 4 or 5, and the holes add up to 72.
    Find the length of each hole."""
    n_holes = 18  # the course has 18 holes
    lengths = [3, 4, 5]  # the possible lengths of a hole
    total_length = 72  # the lengths of all holes add up to this

    # is_length[i][v] is true when hole i is v long
    is_length = [{v: Bool(f"hole_{i}_len_{v}") for v in lengths} for i in range(n_holes)]
    constraints = []

    # Each hole has exactly one length.
    constraints += [sum(is_length[i].values()) == 1 for i in range(n_holes)]

    # The holes add up to the length of the course.
    constraints.append(
        sum(v * is_length[i][v] for i in range(n_holes) for v in lengths) == total_length
    )

    # holes[i] is the length of hole i
    holes = [sum(v * is_length[i][v] for v in lengths) for i in range(n_holes)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"holes": holes}


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
