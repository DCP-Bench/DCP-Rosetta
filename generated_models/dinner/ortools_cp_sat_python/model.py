# dinner: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install ortools`) with:
#   python dinner.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Twenty people go to dinner, grandparents, parents and children, and the
    bill is $20: how many of each go?"""
    model = cp_model.CpModel()

    # The number of grandparents (1 to 6), parents (1 to 10) and children (1 to 40) at dinner
    n_grandparents = model.new_int_var(1, 6, "grandparents")
    n_parents = model.new_int_var(1, 10, "parents")
    n_children = model.new_int_var(1, 40, "children")

    # The bill is $20, counted in half dollars: 40 half dollars in all. A grandparent
    # costs 6 half dollars ($3), a parent 4 ($2) and a child 1 ($0.50).
    model.add(n_grandparents * 6 + n_parents * 4 + n_children * 1 == 20 * 2)
    # There are 20 people in total.
    model.add(n_grandparents + n_parents + n_children == 20)

    return model, {
        "grandparents": n_grandparents,
        "parents": n_parents,
        "children": n_children,
    }


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
