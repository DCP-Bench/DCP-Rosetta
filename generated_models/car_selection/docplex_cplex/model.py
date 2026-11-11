# car_selection: a CPLEX (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python car_selection.py car_selection.json

from docplex.mp.model import Model


def create_model(instance):
    """Car selection: assign participants to cars they are interested in, as many pairs as possible."""
    interested = instance["possible_assignments"]  # interested[i][j] is 1 if participant i likes car j
    participants = range(len(interested))
    cars = range(len(interested[0]))

    model = Model("car_selection")

    # assign[i, j] is 1 when participant i gets car j. A car the participant is
    # not interested in gets an upper bound of 0, so it can never be assigned.
    assign = model.binary_var_matrix(participants, cars, name="assign")
    for i in participants:
        for j in cars:
            assign[i, j].ub = interested[i][j]

    # Each participant is assigned to at most one car.
    model.add_constraints(model.sum(assign[i, j] for j in cars) <= 1 for i in participants)

    # Each car is assigned to at most one participant.
    model.add_constraints(model.sum(assign[i, j] for i in participants) <= 1 for j in cars)

    # Maximise the number of assignments.
    model.maximize(model.sum(assign.values()))

    return model, {"assignments": [[assign[i, j] for j in cars] for i in participants]}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
