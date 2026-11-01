# hanging_weights: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install ortools`) with:
#   python hanging_weights.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Thirteen weights A to M, each an integer from 1 to 13, hang from a system of
    bars. Find the weights that make every pivot balance, where the weights on either
    side of a pivot are equal when weighted by their distance from the pivot."""
    model = cp_model.CpModel()

    # x[0..12] are the weights A to M, each an integer from 1 to 13
    x = [model.new_int_var(1, 13, name) for name in "abcdefghijklm"]
    a, b, c, d, e, f, g, h, i, j, k, l, m = x

    # The thirteen weights are distinct.
    model.add_all_different(x)

    # Bottom right bar, balanced on its pivot: 5*C = D.
    model.add(5 * c == d)
    # Bottom left bar: 4*A = B.
    model.add(4 * a == b)
    # Bar holding E and F: 3*E = 2*F.
    model.add(3 * e == 2 * f)
    # A bar hanging under another bar counts as one weight equal to its total load,
    # so the bar holding G has the whole C-D bar on one side.
    model.add(3 * g == 2 * (c + d))
    # The bar holding J and K has the A-B bar and the G bar (with C and D) hanging
    # from it.
    model.add(3 * (a + b) + 2 * j == k + 2 * (g + c + d))
    # The bar holding H and I has the E-F bar hanging from it.
    model.add(3 * h == 2 * (e + f) + 3 * i)
    # The bar holding L and M has the H-I bar (with E and F) hanging from it.
    model.add(h + i + e + f == l + 4 * m)
    # The top bar balances the L-M side against the J-K side.
    model.add(4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d))

    return model, {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
                   "h": h, "i": i, "j": j, "k": k, "l": l, "m": m}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
