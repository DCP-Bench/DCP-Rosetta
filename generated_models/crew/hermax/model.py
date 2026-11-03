# crew: a hermax (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install hermax`):
#   python crew.py crew.json

from hermax.model import Model


def create_model(instance):
    """Staff 10 flights with cabin crew from a pool of 20 flight attendants. Each flight needs
    a given number of crew, and at least a given number of them with each attribute (steward,
    hostess, French, Spanish, German). An attendant who works a flight has the next two flights
    off, so no attendant works two flights that are at most two apart. Find an assignment that
    meets all of this."""
    attributes = instance["attributes"]    # attributes[p][a]: 1 if attendant p has attribute a (steward, hostess, French, Spanish, German)
    required = instance["required_crew"]   # required[f][0]: crew size of flight f; required[f][a + 1]: minimum number of crew with attribute a on flight f
    n_persons = len(attributes)            # number of flight attendants
    n_flights = len(required)              # number of flights
    n_attributes = len(attributes[0])      # number of attributes per attendant

    m = Model()

    # crew[f][p] is true when attendant p is assigned to flight f
    crew = m.bool_matrix("crew", n_flights, n_persons)

    for f in range(n_flights):
        # Flight f has exactly the number of crew it needs.
        m &= (sum(crew[f][p] for p in range(n_persons)) == required[f][0])
        # Flight f has at least the required number of crew with each attribute.
        for a in range(n_attributes):
            holders = [p for p in range(n_persons) if attributes[p][a]]
            if required[f][a + 1] > 0:
                m &= (sum(crew[f][p] for p in holders) >= required[f][a + 1])

    # Rest rule: after working a flight, an attendant has the next two flights off.
    # So no attendant works two flights among any three consecutive flights.
    for p in range(n_persons):
        for start in range(n_flights):
            window = range(start, min(start + 3, n_flights))
            if len(window) > 1:
                m &= (sum(crew[f][p] for f in window) <= 1)

    # No objective: any assignment that meets the requirements is a solution.
    return m, {"crew": crew}


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
