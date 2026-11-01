# abbots_puzzle: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install ortools`) with:
#   python abbots_puzzle.py

from ortools.sat.python import cp_model


def create_model(instance):
    """100 bushels of corn are distributed among 100 people: each man receives
    three bushels, each woman two and each child half a bushel, and there are
    five times as many women as men. Find the number of men, women and children."""
    model = cp_model.CpModel()

    # The number of men.
    n_men = model.new_int_var(0, 100, "men")
    # The number of women.
    n_women = model.new_int_var(0, 100, "women")
    # The number of children.
    n_children = model.new_int_var(0, 100, "children")

    # There are 100 people.
    model.add(n_men + n_women + n_children == 100)
    # The bushels add up to 100: each man gets 3, each woman 2 and each child half a bushel.
    model.add(n_men * 6 + n_women * 4 + n_children == 200)
    # There are five times as many women as men.
    model.add(n_women == n_men * 5)

    return model, {"men": n_men, "women": n_women, "children": n_children}


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
