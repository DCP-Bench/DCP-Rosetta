# cur_num: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install ortools`) with:
#   python cur_num.py

from ortools.sat.python import cp_model


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    model = cp_model.CpModel()

    # peculiar is the number to find
    peculiar = model.new_int_var(1, 10000, "peculiar")
    # plus_one is peculiar + 1, and root_plus_one times itself is plus_one
    plus_one = model.new_int_var(1, 10000, "plus_one")
    root_plus_one = model.new_int_var(1, 10000, "root_plus_one")
    # half is peculiar / 2, and half_plus_one is half + 1
    half = model.new_int_var(1, 10000, "half")
    half_plus_one = model.new_int_var(1, 10000, "half_plus_one")
    # root_half_plus_one times itself is half_plus_one
    root_half_plus_one = model.new_int_var(1, 10000, "root_half_plus_one")

    # The number is not 48, the known example.
    model.add(peculiar != 48)

    # Adding 1 to it gives a square number.
    model.add(peculiar + 1 == plus_one)
    model.add_multiplication_equality(plus_one, [root_plus_one, root_plus_one])

    # Halving it and adding 1 gives a square number too.
    model.add(peculiar == 2 * half)
    model.add(half + 1 == half_plus_one)
    model.add_multiplication_equality(half_plus_one, [root_half_plus_one, root_half_plus_one])

    return model, {"peculiar": peculiar}


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
