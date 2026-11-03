# csplib_009_perfect_square_placement: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from itertools import combinations

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def at_least(coordinate, value):
    """The condition that the coordinate is at least value. It is True or False when the
    coordinate's range already decides it."""
    if value <= coordinate.lb:
        return True
    if value > coordinate.ub:
        return False
    return coordinate.ge(value)


def at_most(coordinate, value):
    """The condition that the coordinate is at most value."""
    return negate(at_least(coordinate, value + 1))


def negate(condition):
    return (not condition) if isinstance(condition, bool) else -condition


def add_clause(cnf, *conditions):
    """Require that at least one of the conditions holds. A condition that is True satisfies
    the requirement, and a condition that is False is left out."""
    kept = []
    for condition in conditions:
        if condition is True:
            return
        if condition is not False:
            kept.append(condition)
    cnf.append(kept)


def create_model(instance):
    """Pack squares of the given whole-number sides into a big square of side base, so that
    no two squares overlap, all borders are parallel to the big square, and the squares
    leave no gap."""
    base = instance["base"]    # side of the big square
    sides = instance["sides"]  # sides[i]: side of small square i
    n_squares = len(sides)

    pool = IDPool()

    # x[i] and y[i]: the lower-left corner of square i, counted from 0 along each side. The
    # square lies inside the big square, so the corner is at most base minus its side.
    x = [Integer(f"x{i}", 0, base - sides[i], encoding="coupled", vpool=pool)
         for i in range(n_squares)]
    y = [Integer(f"y{i}", 0, base - sides[i], encoding="coupled", vpool=pool)
         for i in range(n_squares)]

    # The corners take one whole-number value each; these clauses tie the values together.
    engine = IntegerEngine(vars=x + y, vpool=pool)
    cnf = engine.clausify()

    def before(key, a, b, side_a):
        """The condition that square a lies entirely before square b along one side, that
        is a + side_a <= b. Required: for every value t of a, if a is at least t then b is
        at least t + side_a."""
        selector = pool.id(key)
        for t in range(a.lb, a.ub + 1):
            add_clause(cnf, -selector, negate(at_least(a, t)), at_least(b, t + side_a))
        return selector

    # No two squares overlap: for each pair, one lies entirely to the left of the other,
    # or entirely below it.
    for a, b in combinations(range(n_squares), 2):
        cnf.append([before(("left", a, b), x[a], x[b], sides[a]),
                    before(("left", b, a), x[b], x[a], sides[b]),
                    before(("below", a, b), y[a], y[b], sides[a]),
                    before(("below", b, a), y[b], y[a], sides[b])])

    # Implied rule that speeds up the search. The areas add up to the area of the big square,
    # so every unit-wide column and every unit-high row of the big square is covered by
    # squares whose sides add up to exactly base.
    for axis, corner in (("column", x), ("row", y)):
        for c in range(base):
            # open_covers: squares that may or may not cover line c, with their sides;
            # fixed_side: total side of the squares that surely cover it.
            open_covers, open_sides, fixed_side = [], [], 0
            for i in range(n_squares):
                # Square i covers line c exactly when its corner lies in (c - side, c].
                starts_after = at_least(corner[i], c - sides[i] + 1)
                starts_by = at_most(corner[i], c)
                if starts_after is True and starts_by is True:
                    fixed_side += sides[i]
                    continue
                if starts_after is False or starts_by is False:
                    continue
                covers = pool.id((axis, c, i))
                add_clause(cnf, -covers, starts_after)
                add_clause(cnf, -covers, starts_by)
                add_clause(cnf, covers, negate(starts_after), negate(starts_by))
                open_covers.append(covers)
                open_sides.append(sides[i])
            if open_covers:
                cnf.extend(PBEnc.equals(lits=open_covers, weights=open_sides,
                                        bound=base - fixed_side, vpool=pool).clauses)

    return cnf, {"x_coords": x, "y_coords": y}


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
