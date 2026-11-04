# four_islands: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python four_islands.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Four islands, Pwana, Quero, Rayou and Skern, lie on a map laid out as A B over C D.
    Each has a different primary export and tourist attraction. Find the name, export and
    attraction of each island from six clues."""
    # The puzzle states its own map and clues, so instance is not used.
    positions = range(4)  # the map positions A, B, C, D

    def row(p):
        # A and B form the top row, C and D the bottom row.
        return p // 2

    def col(p):
        # A and C form the left column, B and D the right column.
        return p % 2

    def placement(name, count):
        # at[i][p] is true when the i-th thing sits at map position p.
        return [[Bool(f"{name}_{i}_{p}") for p in positions] for i in range(count)]

    def one_position_each(at):
        # Each thing sits at exactly one map position, and no two share one.
        count = len(at)
        return ([sum(at[i]) == 1 for i in range(count)]
                + [sum(at[i][p] for i in range(count)) == 1 for p in positions])

    def clue(x, y, holds):
        # The thing at x and the thing at y are placed so that holds(p, q) is true.
        # Every pair of positions that breaks the clue is ruled out.
        return [~(x[p] & y[q]) for p in positions for q in positions if not holds(p, q)]

    # island_at[k][p] is true when island k is at map position p.
    # The islands are Pwana, Quero, Rayou and Skern, in that order.
    island_at = placement("isl", 4)
    # export_at[j][p] is true when the island with export j is at map position p.
    # The exports are alabaster, bananas, coconuts and durian fruit, in that order.
    export_at = placement("exp", 4)
    # attraction_at[j][p] is true when the island with attraction j is at map position p.
    # The attractions are resort hotel, ice skating rink, jai alai stadium and koala preserve.
    attraction_at = placement("att", 4)

    # The islands, the exports and the attractions each fill the four map positions.
    subject_to = one_position_each(island_at) + one_position_each(export_at) + one_position_each(attraction_at)

    # The koala preserve is due south of Pwana.
    subject_to += clue(island_at[0], attraction_at[3], lambda p, q: col(p) == col(q) and row(q) == row(p) + 1)

    # The alabaster quarry is due west of Quero.
    subject_to += clue(export_at[0], island_at[1], lambda p, q: row(p) == row(q) and col(p) < col(q))

    # The resort hotel is due east of the durian fruit exporter.
    subject_to += clue(attraction_at[0], export_at[3], lambda p, q: row(p) == row(q) and col(p) > col(q))

    # Skern and the jai alai stadium are joined by a north-south bridge.
    subject_to += clue(island_at[3], attraction_at[2], lambda p, q: col(p) == col(q) and row(p) != row(q))

    # Rayou and the banana exporter are joined by an east-west bridge.
    subject_to += clue(island_at[2], export_at[1], lambda p, q: row(p) == row(q) and col(p) != col(q))

    # The ice skating rink and the jai alai stadium are not joined by a bridge.
    subject_to += clue(attraction_at[1], attraction_at[2], lambda p, q: row(p) != row(q) and col(p) != col(q))

    def position_number(at):
        # The map position of each island, export or attraction.
        return [sum(p * at[i][p] for p in positions) for i in range(len(at))]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {
        "island": position_number(island_at),
        "export": position_number(export_at),
        "attraction": position_number(attraction_at),
    }


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
