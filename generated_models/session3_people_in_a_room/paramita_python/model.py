# session3_people_in_a_room: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session3_people_in_a_room.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an entry order
    such that the ratio of females to males in the room is never above 7/3."""
    n_people = 13  # the people who enter the room
    n_males = 4    # how many of them are male

    # sequence[i] is true when the (i + 1)-th person to enter is female
    sequence = [Bool(f"sequence_{i}") for i in range(n_people)]

    # the conditions every entry order must meet
    constraints = []
    # There are n_people - n_males females.
    constraints.append(sum(sequence) == n_people - n_males)
    # After each entry, the females in the room are at most 7/3 of the males.
    # With k people in the room the males are the rest, so this is 10 * females <= 7 * k.
    constraints += [sum(10 * b for b in sequence[:k]) <= 7 * k for k in range(1, n_people + 1)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"sequence": sequence}


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
