# crew: a SCIP (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python crew.py crew.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a given number of
    cabin crew, and at least a given number of stewards, hostesses and speakers
    of each language among them. Someone who works a flight has the next two
    flights off."""
    # required_crew[f]: [crew size, stewards, hostesses, French, Spanish, German]
    # needed on flight f; the crew size is taken as exact, the others as minimum counts
    required = np.array(instance["required_crew"])

    # attributes[p]: [steward, hostess, French, Spanish, German] of person p,
    # 1 where the attendant has the attribute and 0 where not
    attributes = np.array(instance["attributes"])

    n_flights, n_people = len(required), len(attributes)

    model = Model("crew")

    # x[f, p] is 1 when person p is assigned to flight f, and 0 when not
    x = model.addMatrixVar((n_flights, n_people), vtype="B", name="x")

    # Each flight has exactly its crew size of people on it.
    model.addMatrixCons(x.sum(axis=1) == required[:, 0])

    # Each flight has at least the required number of stewards, hostesses and
    # speakers of each language among its people; skills[f, k] counts the people
    # on flight f with attribute k, in the column order of attributes.
    skills = x @ attributes
    model.addMatrixCons(skills >= required[:, 1:])

    # After working a flight, a person has the next two flights off. Row f of
    # x[:-gap] and row f of x[gap:] are flights f and f + gap, so for gap 1 and
    # gap 2 this allows at most one of each such pair to be worked by a person.
    for gap in (1, 2):
        model.addMatrixCons(x[:-gap] + x[gap:] <= 1)

    # The problem has no objective: any assignment that meets the rules is an answer.

    return model, {"crew": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
