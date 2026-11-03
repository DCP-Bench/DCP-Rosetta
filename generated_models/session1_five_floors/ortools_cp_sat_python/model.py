# session1_five_floors: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install ortools`) with:
#   python session1_five_floors.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live in a five-floor apartment
    house; find the floor of each from the clues."""
    model = cp_model.CpModel()

    # The floor where each person lives. Baker is not on the fifth floor, Cooper
    # is not on the first, and Fletcher is on neither the first nor the fifth.
    baker = model.new_int_var(1, 4, "B")
    cooper = model.new_int_var(2, 5, "C")
    fletcher = model.new_int_var(2, 4, "F")
    miller = model.new_int_var(1, 5, "M")
    smith = model.new_int_var(1, 5, "S")

    # Everyone lives on a different floor.
    model.add_all_different([baker, cooper, fletcher, miller, smith])

    # Miller lives on a higher floor than Cooper.
    model.add(miller > cooper)

    # Smith does not live on a floor adjacent to Fletcher's.
    model.add(smith != fletcher + 1)
    model.add(smith != fletcher - 1)

    # Fletcher does not live on a floor adjacent to Cooper's.
    model.add(fletcher != cooper + 1)
    model.add(fletcher != cooper - 1)

    return model, {"B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith}


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
