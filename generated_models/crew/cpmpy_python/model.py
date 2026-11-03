# crew: a CPMpy model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python crew.py crew.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a certain number of cabin
    crew, and they have to speak certain languages. Every cabin crew member has two
    flights off after an attended flight."""
    # attributes[p]: whether person p is a steward, a hostess and speaks French, Spanish
    # and German (1 if so, 0 if not)
    attributes = np.array(instance["attributes"])
    # required_crew[f]: the number of crew flight f needs, then the minimum number of
    # stewards, hostesses and speakers of French, Spanish and German among them
    required_crew = np.array(instance["required_crew"])
    n_persons, n_attributes = attributes.shape
    n_flights = len(required_crew)

    # crew[f, p] is true when person p works on flight f
    crew = cp.boolvar(shape=(n_flights, n_persons), name="crew")

    model = cp.Model()
    for f in range(n_flights):
        # Flight f has exactly as many crew members as it needs.
        model.add(cp.sum(crew[f]) == required_crew[f, 0])
        # Among them, flight f has at least the required number of people with each attribute.
        for a in range(n_attributes):
            model.add(cp.sum(crew[f] * attributes[:, a]) >= required_crew[f, a + 1])

    # A person who works on a flight has the next two flights off, so works on at most one
    # of any three consecutive flights.
    for f in range(n_flights - 2):
        model.add(crew[f:f + 3].sum(axis=0) <= 1)

    return model, {"crew": crew}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
