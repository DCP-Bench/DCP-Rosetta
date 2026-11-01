# crew: a Choco-solver (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python crew.py crew.json

from pychoco.model import Model


def create_model(instance):
    """Staff each flight with cabin crew from a pool of flight attendants. A flight needs a given number of crew, with a minimum number of stewards, hostesses and speakers of French, Spanish and German. An attendant who works a flight has the next two flights off."""
    attributes = instance["attributes"]   # attributes[p]: the attributes of attendant p, in the order steward, hostess, French, Spanish, German; 1 if the attendant has it, 0 if not
    required = instance["required_crew"]  # required[f]: the crew size of flight f, then the fewest crew with each attribute on that flight
    n_persons = len(attributes)
    n_flights = len(required)
    n_attributes = len(attributes[0])

    model = Model()

    # crew[f][p] is true when attendant p works flight f
    crew = [[model.boolvar(name=f"crew_{f}_{p}") for p in range(n_persons)] for f in range(n_flights)]

    for f in range(n_flights):
        # Flight f has exactly its crew size of attendants.
        model.sum(crew[f], "=", required[f][0]).post()
        # Among them, at least the required number of attendants have each attribute.
        for a in range(n_attributes):
            model.scalar(crew[f], [attributes[p][a] for p in range(n_persons)], ">=", required[f][a + 1]).post()

    # After a flight, an attendant has the next two flights off, so works at most one of any three consecutive flights.
    for f in range(n_flights - 2):
        for p in range(n_persons):
            model.sum([crew[f][p], crew[f + 1][p], crew[f + 2][p]], "<=", 1).post()

    return model, {"crew": crew}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
