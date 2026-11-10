# csplib_014_solitaire_battleships: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

from paramita.containers import CnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, Iff, Or, add_to_container, to_cnf


def create_model(instance):
    """Solitaire battleships: fill the grid with water and ship parts so that the fleet
    has the given number of ships of each length, no two ships touch (not even
    diagonally), every row and column has the given number of ship squares, and the
    shots hold."""
    n_rows = instance["rows"]          # the number of rows in the grid
    n_cols = instance["cols"]          # the number of columns in the grid
    rowsum = instance["rowsum"]        # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]        # colsum[c]: the number of ship squares in column c
    fleet = instance["fleet_counts"]   # the ships to place: their length and how many of each
    hints = instance["hints"]          # the squares the shots show: their row, column and kind

    names = ["WATER", "CIRCLE", "LEFT", "RIGHT", "TOP", "BOTTOM", "MIDDLE"]  # the kinds of square
    code = {k: instance[k] for k in names}     # code[k]: the number the grid shows for a square of kind k
    by_code = {v: k for k, v in code.items()}  # the kind of square a grid number stands for
    occupied = [k for k in names if k != "WATER"]  # the kinds of square that hold a ship or submarine

    # kind[r][c][k] is true when square (r, c) is of kind k
    kind = [[{k: Bool(f"kind_{r}_{c}_{k}") for k in names} for c in range(n_cols)] for r in range(n_rows)]

    def inside(r, c):
        """Whether square (r, c) lies on the grid."""
        return 0 <= r < n_rows and 0 <= c < n_cols

    def conj(terms):
        """All of the terms hold."""
        return terms[0] if len(terms) == 1 else And(terms)

    def disj(terms):
        """At least one of the terms holds."""
        return terms[0] if len(terms) == 1 else Or(terms)

    def way(r, c, waters, nexts):
        """A way for square (r, c) to be a ship part: the squares at the offsets in `waters`
        are water, and the square at each offset in `nexts`, given as (offset, kinds), is one
        of those kinds. None when one of the required squares lies off the grid."""
        terms = [kind[r + dr][c + dc]["WATER"] for dr, dc in waters if inside(r + dr, c + dc)]
        for (dr, dc), kinds in nexts:
            if not inside(r + dr, c + dc):
                return None
            terms.append(disj([kind[r + dr][c + dc][k] for k in kinds]))
        return conj(terms)

    def require(r, c, piece, *ways):
        """Square (r, c) can be `piece` only if one of the ways holds. A way of None cannot hold."""
        ways = [w for w in ways if w is not None]
        if not ways:
            return ~kind[r][c][piece]
        return If(kind[r][c][piece], disj(ways))

    all8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # the squares around a square

    constraints = []

    # Each square is of exactly one kind.
    for r in range(n_rows):
        for c in range(n_cols):
            constraints.append(sum(kind[r][c][k] for k in names) == 1)

    # Ships do not touch, not even diagonally: every square of a ship has water around it,
    # except the squares of the same ship that continue it in its line.
    for r in range(n_rows):
        for c in range(n_cols):
            # A submarine has water all around it.
            constraints.append(require(r, c, "CIRCLE", way(r, c, all8, [])))
            # The left end of a horizontal ship continues to its right.
            constraints.append(require(r, c, "LEFT",
                                       way(r, c, [o for o in all8 if o != (0, 1)], [((0, 1), ["RIGHT", "MIDDLE"])])))
            # The right end of a horizontal ship continues to its left.
            constraints.append(require(r, c, "RIGHT",
                                       way(r, c, [o for o in all8 if o != (0, -1)], [((0, -1), ["LEFT", "MIDDLE"])])))
            # The top end of a vertical ship continues downwards.
            constraints.append(require(r, c, "TOP",
                                       way(r, c, [o for o in all8 if o != (1, 0)], [((1, 0), ["BOTTOM", "MIDDLE"])])))
            # The bottom end of a vertical ship continues upwards.
            constraints.append(require(r, c, "BOTTOM",
                                       way(r, c, [o for o in all8 if o != (-1, 0)], [((-1, 0), ["TOP", "MIDDLE"])])))
            # A middle part has ship parts on both sides in a horizontal ship, or above and below in a vertical one.
            constraints.append(require(r, c, "MIDDLE",
                                       way(r, c, [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)],
                                           [((0, -1), ["LEFT", "MIDDLE"]), ((0, 1), ["RIGHT", "MIDDLE"])]),
                                       way(r, c, [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1)],
                                           [((-1, 0), ["TOP", "MIDDLE"]), ((1, 0), ["BOTTOM", "MIDDLE"])])))

    # The fleet has the given number of ships of each length. Each ship is counted once, at its first square.
    for length, count in fleet:
        if length == 1:
            # A submarine is a single square.
            starts = [kind[r][c]["CIRCLE"] for r in range(n_rows) for c in range(n_cols)]
        else:
            starts = []
            # A horizontal ship starts at its left end, has middle parts, and ends at its right end.
            # A vertical ship starts at its top end and ends at its bottom end.
            for r in range(n_rows):
                for c in range(n_cols):
                    if inside(r, c + length - 1):
                        # is true when a horizontal ship of this length starts at (r, c)
                        across = Bool(f"across_{length}_{r}_{c}")
                        parts = [kind[r][c]["LEFT"]] + [kind[r][c + k]["MIDDLE"] for k in range(1, length - 1)] \
                            + [kind[r][c + length - 1]["RIGHT"]]
                        constraints.append(Iff(across, And(parts)))
                        starts.append(across)
                    if inside(r + length - 1, c):
                        # is true when a vertical ship of this length starts at (r, c)
                        down = Bool(f"down_{length}_{r}_{c}")
                        parts = [kind[r][c]["TOP"]] + [kind[r + k][c]["MIDDLE"] for k in range(1, length - 1)] \
                            + [kind[r + length - 1][c]["BOTTOM"]]
                        constraints.append(Iff(down, And(parts)))
                        starts.append(down)
        constraints.append(sum(starts) == count)

    # Each row and column has the given number of ship squares.
    for r in range(n_rows):
        constraints.append(sum(kind[r][c][k] for c in range(n_cols) for k in occupied) == rowsum[r])
    for c in range(n_cols):
        constraints.append(sum(kind[r][c][k] for r in range(n_rows) for k in occupied) == colsum[c])

    # The shots show the kind of their squares.
    for r, c, value in hints:
        constraints.append(kind[r][c][by_code[value]])

    # grid[r][c]: the grid number of square (r, c)
    grid = [[sum(code[k] * kind[r][c][k] for k in occupied) for c in range(n_cols)] for r in range(n_rows)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"grid": grid}


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
