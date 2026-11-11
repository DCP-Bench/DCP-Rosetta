# appointment_scheduling: a CPLEX (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python appointment_scheduling.py appointment_scheduling.json

from docplex.mp.model import Model


def create_model(instance):
    """Appointment scheduling: give each person their own interview slot at a time they are free."""
    free = instance["m"]  # free[i][j] is 1 if person i is free in slot j
    people = range(len(free))
    slots = range(len(free[0]))

    model = Model("appointment_scheduling")

    # x[i, j] is 1 when person i is interviewed in slot j
    x = model.binary_var_matrix(people, slots, name="x")

    # Each person gets exactly one slot.
    model.add_constraints(model.sum(x[i, j] for j in slots) == 1 for i in people)

    # Each slot goes to exactly one person.
    model.add_constraints(model.sum(x[i, j] for i in people) == 1 for j in slots)

    # A person is only given a slot in which they are free.
    model.add_constraints(x[i, j] <= free[i][j] for i in people for j in slots)

    return model, {"x": [[x[i, j] for j in slots] for i in people]}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
