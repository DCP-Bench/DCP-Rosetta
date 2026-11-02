# crew: a cvc5 (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python crew.py crew.json

import cvc5.pythonic as c5


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a certain number of cabin
    crew, and they have to speak certain languages. Every cabin crew member has two
    flights off after an attended flight."""
    # attributes[p][a] is 1 when person p has attribute a, in the order steward, hostess,
    # French, Spanish, German, and 0 otherwise
    attributes = instance["attributes"]
    # required_crew[f][0] is the crew size flight f needs; required_crew[f][a + 1] is the
    # fewest crew with attribute a that flight f needs
    required_crew = instance["required_crew"]
    n_people = len(attributes)
    n_flights = len(required_crew)
    n_attributes = len(attributes[0])

    # crew[f][p] is true when person p works on flight f
    crew = [[c5.Bool(f"crew_{f}_{p}") for p in range(n_people)] for f in range(n_flights)]

    solver = c5.Solver()

    # Each flight has exactly as many crew as it needs.
    for f in range(n_flights):
        solver.add(
            c5.Sum([c5.If(crew[f][p], 1, 0) for p in range(n_people)]) == required_crew[f][0]
        )

    # Each flight has enough crew with each attribute.
    for f in range(n_flights):
        for a in range(n_attributes):
            holders = [crew[f][p] for p in range(n_people) if attributes[p][a] == 1]
            if holders:
                solver.add(
                    c5.Sum([c5.If(h, 1, 0) for h in holders]) >= required_crew[f][a + 1]
                )

    # A crew member who works a flight has the next two flights off.
    for p in range(n_people):
        for f in range(n_flights):
            for g in (f + 1, f + 2):
                if g < n_flights:
                    solver.add(c5.Not(c5.And(crew[f][p], crew[g][p])))

    return solver, {"crew": crew}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
