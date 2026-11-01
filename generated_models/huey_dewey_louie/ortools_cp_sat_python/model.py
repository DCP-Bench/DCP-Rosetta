# huey_dewey_louie: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install ortools`) with:
#   python huey_dewey_louie.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Huey, Dewey and Louie are cub scouts questioned by their uncle; they cannot lie,
    so each of their statements is true. Who is guilty?"""
    model = cp_model.CpModel()

    # huey, dewey, louie: whether each of them is guilty
    huey = model.new_bool_var("huey")
    dewey = model.new_bool_var("dewey")
    louie = model.new_bool_var("louie")

    # Huey: Dewey and Louie have an equal share, so one is guilty exactly when the other is.
    model.add(dewey == louie)
    # Dewey: if Huey is guilty, then so am I.
    model.add_implication(huey, dewey)
    # Louie: Dewey and I are not both guilty.
    model.add_bool_or([~dewey, ~louie])

    return model, {"huey": huey, "dewey": dewey, "louie": louie}


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
