# crew: an Exact (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python crew.py crew.json

from exact import Exact


def create_model(instance):
    """Staff ten flights with flight attendants. Each flight needs a set number of cabin
    crew, and enough of them must have the languages and roles it requires. A person who
    works a flight has the next two flights off."""
    # attributes[p][a] is 1 when person p has attribute a, and 0 when not. The attributes
    # are steward, hostess, French, Spanish and German, in that order.
    attributes = instance["attributes"]
    # required[f][0] is the crew size flight f needs. The next entries are the fewest crew
    # with each attribute, in the same order.
    required = instance["required_crew"]

    n_persons = len(attributes)        # the number of flight attendants
    n_flights = len(required)          # the number of flights
    n_attributes = len(attributes[0])  # the number of attributes

    solver = Exact()

    # Exact identifies its variables by name.
    # crew[f][p] is 1 when person p works flight f, and 0 when not.
    crew = [[f"crew_{f}_{p}" for p in range(n_persons)] for f in range(n_flights)]
    for row in crew:
        for name in row:
            solver.addVariable(name, 0, 1)

    for f in range(n_flights):
        # Flight f has exactly the crew it needs.
        solver.addConstraint([(1, name) for name in crew[f]], True, required[f][0],
                             True, required[f][0])
        for a in range(n_attributes):
            # the crew on flight f who have attribute a
            skilled = [(1, crew[f][p]) for p in range(n_persons) if attributes[p][a]]
            # Flight f has at least the required number of crew with attribute a.
            solver.addConstraint(skilled, True, required[f][a + 1])

    # A person who works a flight has the next two flights off, so works at most one of
    # any three flights in a row.
    for f in range(n_flights - 2):
        for p in range(n_persons):
            solver.addConstraint([(1, crew[f][p]), (1, crew[f + 1][p]), (1, crew[f + 2][p])],
                                 False, 0, True, 1)

    return solver, {"crew": crew}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
