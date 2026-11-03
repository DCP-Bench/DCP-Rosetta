# car_selection: a hermax (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install hermax`):
#   python car_selection.py car_selection.json

from hermax.model import Model


def create_model(instance):
    """Assign participants to cars so that the number of assignments is as large as possible.
    Each participant may be interested in only some cars, and each participant gets at most
    one car and each car goes to at most one participant."""
    # possible[i][j] = 1 if participant i is interested in car j, 0 otherwise
    possible = instance["possible_assignments"]
    n_participants = len(possible)     # the number of participants (rows)
    n_cars = len(possible[0])          # the number of cars (columns)

    m = Model()

    # assignments[i][j] is true when participant i is assigned to car j
    assignments = m.bool_matrix("assignments", n_participants, n_cars)

    # Each participant is assigned to at most one car.
    for i in range(n_participants):
        m &= assignments.row(i).at_most_one()

    # Each car is assigned to at most one participant.
    for j in range(n_cars):
        m &= assignments.col(j).at_most_one()

    # A participant can only be assigned to a car they are interested in.
    for i in range(n_participants):
        for j in range(n_cars):
            if not possible[i][j]:
                m &= ~assignments[i][j]

    # Maximise the number of assignments. hermax always minimises, so minimise the negated count.
    m.obj += -sum(assignments[i][j]
                  for i in range(n_participants) for j in range(n_cars)
                  if possible[i][j])

    return m, {"assignments": assignments}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
