# csplib_009_perfect_square_placement: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Place squares with the given integer sides inside a square board of side `base`, with
    their borders parallel to the board's and no two squares overlapping. Report the
    lower-left corner of every square, counting from 0."""
    base = instance["base"]    # the side length of the board
    sides = instance["sides"]  # sides[i]: the side length of square i
    n = len(sides)

    m = Model()

    # x[i] is the column of the lower-left corner of square i, 0..base - sides[i]
    x = [m.int(f"x_{i}", 0, base - sides[i]) for i in range(n)]
    # y[i] is the row of the lower-left corner of square i, 0..base - sides[i]
    y = [m.int(f"y_{i}", 0, base - sides[i]) for i in range(n)]

    # No two squares overlap: for every pair (i, j), square i lies left of, right of,
    # below or above square j. One of the four Booleans below must be true.
    for i in range(n):
        for j in range(i + 1, n):
            left = m.bool()   # i is entirely left of j
            right = m.bool()  # i is entirely right of j
            below = m.bool()  # i is entirely below j
            above = m.bool()  # i is entirely above j
            m &= (left | right | below | above)
            m &= (x[i] + sides[i] <= x[j]).only_if(left)
            m &= (x[j] + sides[j] <= x[i]).only_if(right)
            m &= (y[i] + sides[i] <= y[j]).only_if(below)
            m &= (y[j] + sides[j] <= y[i]).only_if(above)

    # Counting argument. When the squares' areas add up to the board's area, the squares
    # leave no gap, so every unit column and every unit row of the board is covered by
    # squares whose sides add up to exactly `base`. This is implied by the constraints
    # above but shortens the search a lot. The sum of areas comes from the instance data.
    if sum(side * side for side in sides) == base * base:
        for starts in (x, y):
            for c in range(base):
                cover_terms = []  # side * (1 if the square covers unit c, else 0), undetermined squares
                fixed = 0         # total side of the squares that surely cover unit c
                for i in range(n):
                    covers = covers_unit(m, starts[i], sides[i], c)
                    if covers is True:
                        fixed += sides[i]
                    elif covers is not False:
                        cover_terms.append(sides[i] * covers)
                # The squares covering unit c have sides adding up to the board's side.
                if cover_terms:
                    m &= (sum_expr(cover_terms) == base - fixed)

    # No objective: the problem asks only for a placement, so any valid placement is an answer.
    return m, {"x_coords": x, "y_coords": y}


def covers_unit(m, start, side, c):
    """Whether a square with lower-left corner `start` (a variable) and this side covers the unit
    at position c, i.e. start is in c - side + 1 .. c. Returns True or False when the domain
    of `start` already decides it, otherwise a Literal."""
    first, last = c - side + 1, c  # the starts that cover unit c
    if last < start.lb or first > start.ub:
        return False
    if first <= start.lb and last >= start.ub:
        return True
    after_first = True if first <= start.lb else (start >= first)
    before_last = True if last >= start.ub else (start <= last)
    if after_first is True:
        return before_last
    if before_last is True:
        return after_first
    covers = m.bool()
    m &= (after_first & before_last).iff(covers)
    return covers


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
