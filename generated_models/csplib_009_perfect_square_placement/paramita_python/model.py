# csplib_009_perfect_square_placement: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def create_model(instance):
    """Pack squares of the given sides into a big square of side base, with no two squares
    overlapping and all borders parallel to the big square's border. The areas of the small
    squares add up to the area of the big square, so no space is left over. Give the
    lower-left corner of each square, counted from 0, as x_coords and y_coords."""
    base = instance["base"]    # the side of the big square
    sides = instance["sides"]  # sides[i]: the side of square i
    n_squares = len(sides)     # the number of squares

    # Distance of square i from the origin along one axis, from 0 to base - sides[i].
    # The flag at index k - 1 is true when that distance is k or more.
    def distance_flags(axis, i):
        return [Bool(f"{axis}_at_least_{i}_{k}") for k in range(1, base - sides[i] + 1)]

    # A distance of k + 1 or more also means a distance of k or more.
    def in_order(flags):
        return [If(flags[k + 1], flags[k]) for k in range(len(flags) - 1)]

    # If cond holds, the square starting at a ends at or before the square starting at b:
    # the start of a plus side_a is at most the start of b. Returns one constraint per
    # possible start of a.
    def ends_before(cond, a_flags, side_a, b_flags):
        result = []
        for k in range(len(a_flags) + 1):  # a starts at distance k
            m = k + side_a                  # so b starts at distance m or more
            clause = [~cond]
            if k >= 1:
                clause.append(~a_flags[k - 1])
            if m <= len(b_flags):
                clause.append(b_flags[m - 1])
            result.append(clause[0] if len(clause) == 1 else Or(clause))
        return result

    x_flags, y_flags, constraints = [], [], []
    for i in range(n_squares):
        x_flags.append(distance_flags("x", i))
        y_flags.append(distance_flags("y", i))
        constraints += in_order(x_flags[i]) + in_order(y_flags[i])

    # Lower-left corner of square i, from the origin.
    x_coords = [sum(flags) for flags in x_flags]
    y_coords = [sum(flags) for flags in y_flags]

    # Each pair of squares does not overlap: one lies left of the other, or one lies below
    # the other. Four flags per pair say which of these holds.
    for i in range(n_squares):
        for j in range(i + 1, n_squares):
            i_left_of_j = Bool(f"i_left_of_j_{i}_{j}")
            j_left_of_i = Bool(f"j_left_of_i_{i}_{j}")
            i_below_j = Bool(f"i_below_j_{i}_{j}")
            j_below_i = Bool(f"j_below_i_{i}_{j}")
            constraints.append(Or([i_left_of_j, j_left_of_i, i_below_j, j_below_i]))

            # A square that is left of or below another one ends before the other one starts.
            constraints += ends_before(i_left_of_j, x_flags[i], sides[i], x_flags[j])
            constraints += ends_before(j_left_of_i, x_flags[j], sides[j], x_flags[i])
            constraints += ends_before(i_below_j, y_flags[i], sides[i], y_flags[j])
            constraints += ends_before(j_below_i, y_flags[j], sides[j], y_flags[i])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x_coords": x_coords, "y_coords": y_coords}


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
