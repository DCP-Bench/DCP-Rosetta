# circular_table_averbach_1_2: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python circular_table_averbach_1_2.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, add_to_container, to_cnf


def create_model(instance):
    """Three players, X, Y and Z, of different nationalities (American, English and French) sit round
    a table and each passes cards to the person on their right. Find the seat of each player and of
    each nationality, so that a matching seat means the same person."""
    n_seats = 3  # the seats around the table
    # seat s + 1 is on the right of seat s, and seat 0 is on the right of the last seat
    seats = range(n_seats)

    constraints = []

    def seat_vars(name):
        # at[v] is true when the person or nationality `name` sits in seat v
        return {v: Bool(f"{name}_seat_{v}") for v in seats}

    def seat_of(at):
        # the seat as a number
        return sum(v * at[v] for v in seats)

    def one_seat_each(group):
        # each member of the group sits in exactly one seat, and no two share a seat
        for at in group:
            constraints.append(sum(at.values()) == 1)
        for v in seats:
            constraints.append(sum(at[v] for at in group) == 1)

    # the seats of the players X, Y and Z
    x, y, z = seat_vars("X"), seat_vars("Y"), seat_vars("Z")
    # the seats of the American, the English and the French
    american, english, french = seat_vars("american"), seat_vars("english"), seat_vars("french")

    # The three players sit in different seats.
    one_seat_each([x, y, z])

    # The three nationalities sit in different seats.
    one_seat_each([american, english, french])

    # Y passed three hearts to the American, so the American sits on Y's right.
    for v in seats:
        constraints.append(Iff(y[v], american[(v + 1) % n_seats]))

    # X passed to the person on X's right, who passed to the Frenchwoman, so the Frenchwoman
    # sits two seats on from X.
    for v in seats:
        constraints.append(Iff(x[v], french[(v + 2) % n_seats]))

    # the seat of each player and of each nationality
    outputs = {
        "x": seat_of(x),
        "y": seat_of(y),
        "z": seat_of(z),
        "american": seat_of(american),
        "english": seat_of(english),
        "french": seat_of(french),
    }

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
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
