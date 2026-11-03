# csplib_014_solitaire_battleships: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Fill a battleships grid: every cell is water, a submarine or a part of a ship. The ships
    are straight, have the fleet's sizes and never touch, not even diagonally. Each row and
    column has the given number of ship cells, and the revealed cells keep their content."""
    rows = instance["rows"]        # the number of rows
    cols = instance["cols"]        # the number of columns
    rowsum = instance["rowsum"]    # rowsum[r]: the number of ship cells in row r
    colsum = instance["colsum"]    # colsum[c]: the number of ship cells in column c
    fleet = dict(instance["fleet_counts"])  # fleet[size]: the number of ships that are size cells long
    hints = instance["hints"]      # the cells the puzzle reveals, with their content
    WATER = instance["WATER"]      # the code of a water cell
    _SHIP = instance["_SHIP"]      # the code of a ship cell whose part is not stated
    CIRCLE = instance["CIRCLE"]    # the code of a submarine
    LEFT = instance["LEFT"]        # the code of the left part of a ship
    RIGHT = instance["RIGHT"]      # the code of the right part of a ship
    TOP = instance["TOP"]          # the code of the top part of a ship
    BOTTOM = instance["BOTTOM"]    # the code of the bottom part of a ship
    MIDDLE = instance["MIDDLE"]    # the code of a middle part of a ship
    codes = [WATER, _SHIP, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]  # every code a cell can show

    pool = IDPool()

    # grid[r][c] is the content of the cell in row r, column c
    grid = [[Integer(f"grid_{r}_{c}", min(codes), max(codes), vpool=pool) for c in range(cols)]
            for r in range(rows)]
    engine = IntegerEngine(vars=[cell for row in grid for cell in row], vpool=pool)
    cnf = engine.clausify()

    def shows(r, c, *wanted):
        """The condition that the cell at (r, c) shows one of the wanted codes. The cells outside
        the grid are water."""
        if not (0 <= r < rows and 0 <= c < cols):
            return [True] if WATER in wanted else []
        return [grid[r][c].equals(code) for code in wanted]

    def add_clause(*conditions):
        """Require that at least one of the conditions holds. Each condition is a list of
        alternatives from shows, or True or False."""
        clause = []
        for condition in conditions:
            for item in (condition if isinstance(condition, list) else [condition]):
                if item is True:
                    return
                if item is not False:
                    clause.append(item)
        cnf.append(clause)

    def implies(antecedent, *requirements):
        """If the antecedent holds, every requirement holds. Each requirement is a list of
        alternatives from shows."""
        for requirement in requirements:
            add_clause(-antecedent, requirement)

    # The cells the puzzle reveals keep their content.
    for r, c, code in hints:
        cnf.append(shows(r, c, code))

    # non_water[r][c] is true when the cell at (r, c) holds a ship cell or a submarine
    non_water = [[-grid[r][c].equals(WATER) for c in range(cols)] for r in range(rows)]
    # Each row and each column has the given number of ship cells.
    for r in range(rows):
        cnf.extend(CardEnc.equals(lits=non_water[r], bound=rowsum[r], vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    for c in range(cols):
        cnf.extend(CardEnc.equals(lits=[non_water[r][c] for r in range(rows)], bound=colsum[c],
                                  vpool=pool, encoding=EncType.seqcounter).clauses)

    for r in range(rows):
        for c in range(cols):
            ship = non_water[r][c]
            up, down = (r - 1, c), (r + 1, c)
            left, right = (r, c - 1), (r, c + 1)

            # Ships do not touch diagonally: a ship cell has water in its four diagonal corners.
            for dr in (-1, 1):
                for dc in (-1, 1):
                    implies(ship, shows(r + dr, c + dc, WATER))

            # A submarine has water on all four sides.
            for nr, nc in (up, down, left, right):
                implies(grid[r][c].equals(CIRCLE), shows(nr, nc, WATER))

            # A left part has a middle or right part on its right, and water on its other sides.
            implies(grid[r][c].equals(LEFT), shows(*right, MIDDLE, RIGHT), shows(*left, WATER),
                    shows(*up, WATER), shows(*down, WATER))
            # A right part has a middle or left part on its left, and water on its other sides.
            implies(grid[r][c].equals(RIGHT), shows(*left, MIDDLE, LEFT), shows(*right, WATER),
                    shows(*up, WATER), shows(*down, WATER))
            # A top part has a middle or bottom part below it, and water on its other sides.
            implies(grid[r][c].equals(TOP), shows(*down, MIDDLE, BOTTOM), shows(*up, WATER),
                    shows(*left, WATER), shows(*right, WATER))
            # A bottom part has a middle or top part above it, and water on its other sides.
            implies(grid[r][c].equals(BOTTOM), shows(*up, MIDDLE, TOP), shows(*down, WATER),
                    shows(*left, WATER), shows(*right, WATER))

            # A middle part lies across a horizontal ship (horizontal) or a vertical ship (vertical).
            # A horizontal ship has water above and below the middle part, and a vertical one has
            # water on both sides.
            horizontal = pool.id(("horizontal", r, c))
            vertical = pool.id(("vertical", r, c))
            cnf.append([-grid[r][c].equals(MIDDLE), horizontal, vertical])
            implies(horizontal, shows(*left, LEFT, MIDDLE), shows(*right, RIGHT, MIDDLE),
                    shows(*up, WATER), shows(*down, WATER))
            implies(vertical, shows(*up, TOP, MIDDLE), shows(*down, BOTTOM, MIDDLE),
                    shows(*left, WATER), shows(*right, WATER))

    # The fleet has the given number of submarines.
    cnf.extend(CardEnc.equals(lits=[grid[r][c].equals(CIRCLE) for r in range(rows) for c in range(cols)],
                              bound=fleet[1], vpool=pool, encoding=EncType.seqcounter).clauses)

    # A ship of a listed size starts at a cell and runs right or down: a left (top) part, the
    # middle parts, and a right (bottom) part in a line. ship_here is true exactly when that
    # ship is there.
    for size, count in fleet.items():
        if size < 2:
            continue
        # starts: the ship_here selectors of the ships of this size, one per place they can start
        starts = []
        for r in range(rows):
            for c in range(cols):
                for dr, dc, first, last in ((0, 1, LEFT, RIGHT), (1, 0, TOP, BOTTOM)):
                    end_r, end_c = r + dr * (size - 1), c + dc * (size - 1)
                    if end_r >= rows or end_c >= cols:
                        continue
                    parts = [grid[r][c].equals(first), grid[end_r][end_c].equals(last)]
                    parts += [grid[r + dr * k][c + dc * k].equals(MIDDLE) for k in range(1, size - 1)]
                    ship_here = pool.id(("ship", size, r, c, dr))
                    for part in parts:
                        cnf.append([-ship_here, part])
                    cnf.append([ship_here] + [-part for part in parts])
                    starts.append(ship_here)
        # The fleet has the given number of ships of this size.
        cnf.extend(CardEnc.equals(lits=starts, bound=count, vpool=pool, encoding=EncType.seqcounter).clauses)

    # ends: the cells that hold a left or top part
    ends = [grid[r][c].equals(code) for r in range(rows) for c in range(cols) for code in (LEFT, TOP)]
    # Every ship longer than one cell has exactly one left or top part, so there are as many
    # such parts as those ships, and no ship of another size is placed.
    cnf.extend(CardEnc.equals(lits=ends, bound=sum(count for size, count in fleet.items() if size > 1),
                              vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
