# crew: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install ortools`):
#   python crew.py crew.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a certain number of cabin
    crew, and they have to speak certain languages."""
    # attributes[p][a]: whether person p has attribute a (steward, hostess, French, Spanish or German)
    attributes = instance["attributes"]
    # required_crew[f]: the crew size of flight f, then the fewest crew with each attribute that flight needs
    required_crew = instance["required_crew"]
    # columns[a]: attribute a of each person
    columns = list(zip(*attributes))

    model = cp_model.CpModel()

    # crew[f][p] is true when person p is assigned to flight f
    crew = [[model.new_bool_var(f"crew_{f}_{p}") for p in range(len(attributes))] for f in range(len(required_crew))]

    for f, needs in enumerate(required_crew):
        # Flight f has exactly as many crew as it needs.
        model.add(sum(crew[f]) == needs[0])
        # Among them, flight f has enough people with each attribute.
        for column, fewest in zip(columns, needs[1:]):
            model.add(sum(c * x for c, x in zip(column, crew[f])) >= fewest)

    # A person who is on a flight has the next two flights off, so is on at most one of
    # any three consecutive flights.
    for f in range(len(required_crew) - 2):
        for p in range(len(attributes)):
            model.add(sum(crew[f + k][p] for k in range(3)) <= 1)

    return model, {"crew": crew}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
