# packing_rectangles: a Paramita (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python packing_rectangles.py packing_rectangles.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Or, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Place the rectangles inside one box, without overlap and with each rectangle inside
    the box, so that the box has the least possible area."""
    widths = instance["widths"]    # widths[i]: the width of rectangle i
    heights = instance["heights"]  # heights[i]: the height of rectangle i
    n = len(widths)                # number of rectangles

    # The box is never wider or taller than all rectangles placed side by side.
    max_box_width = sum(widths)
    max_box_height = sum(heights)

    def whole_number(name, largest):
        # A whole number from 0 to largest, held as statements "at least k" for k = 1 .. largest.
        # Being at least k + 1 implies being at least k.
        at_least = [Bool(f"{name}_at_least_{k + 1}") for k in range(largest)]
        order = [If(at_least[k + 1], at_least[k]) for k in range(largest - 1)]
        return at_least, order

    # The box width total_x and height total_y.
    box_width, width_order = whole_number("total_x", max_box_width)
    box_height, height_order = whole_number("total_y", max_box_height)
    cons = width_order + height_order
    total_x = sum(box_width)
    total_y = sum(box_height)

    # The box is at least as wide as the widest rectangle and as tall as the tallest one.
    cons += box_width[:max(widths)]
    cons += box_height[:max(heights)]

    # pos_x[i] and pos_y[i] are the lower-left corner of rectangle i.
    pos_x, pos_y = [], []
    for i in range(n):
        x_at_least, x_order = whole_number(f"pos_x_{i}", max_box_width)
        y_at_least, y_order = whole_number(f"pos_y_{i}", max_box_height)
        cons += x_order + y_order
        pos_x.append(sum(x_at_least))
        pos_y.append(sum(y_at_least))

    # Each rectangle lies inside the box: its corner plus its size stays within the box.
    for i in range(n):
        cons.append(pos_x[i] + widths[i] <= total_x)
        cons.append(pos_y[i] + heights[i] <= total_y)

    # No two rectangles overlap: for each pair, one of the four sides separates them.
    for i in range(n):
        for j in range(i + 1, n):
            left = Bool(f"left_{i}_{j}")    # rectangle i lies left of rectangle j
            right = Bool(f"right_{i}_{j}")  # rectangle j lies left of rectangle i
            below = Bool(f"below_{i}_{j}")  # rectangle i lies below rectangle j
            above = Bool(f"above_{i}_{j}")  # rectangle j lies below rectangle i
            cons.append(Or([left, right, below, above]))
            cons.append(If(left, pos_x[i] + widths[i] <= pos_x[j]))
            cons.append(If(right, pos_x[j] + widths[j] <= pos_x[i]))
            cons.append(If(below, pos_y[i] + heights[i] <= pos_y[j]))
            cons.append(If(above, pos_y[j] + heights[j] <= pos_y[i]))

    # unit_square[a][b] is true when the box covers the unit square at column a, row b.
    unit_square = [[Bool(f"unit_square_{a}_{b}") for b in range(max_box_height)]
                   for a in range(max_box_width)]
    for a in range(max_box_width):
        for b in range(max_box_height):
            cons.append(If(box_width[a] & box_height[b], unit_square[a][b]))

    # The box area is the number of unit squares it covers.
    area = sum(sum(row) for row in unit_square)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-area, And(cons), to_cnf, formula, pool)

    return (formula, pool), {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
