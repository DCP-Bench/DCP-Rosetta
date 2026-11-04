# crew: a PuLP (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python crew.py crew.json

import pulp


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a certain number of cabin
    crew, and they have to speak certain languages. Every cabin crew member has two
    flights off after an attended flight."""
    # attributes[p][a]: 1 if person p has attribute a (steward, hostess, French, Spanish or German), 0 if not
    attributes = instance["attributes"]
    # required_crew[f]: the crew size flight f needs, then the fewest people with each attribute it needs
    required_crew = instance["required_crew"]
    n_persons = len(attributes)
    n_flights = len(required_crew)
    n_attributes = len(attributes[0])

    problem = pulp.LpProblem("crew", pulp.LpMinimize)

    # crew[f][p] is 1 when person p is assigned to flight f, and 0 when not
    crew = [[pulp.LpVariable(f"crew_{f}_{p}", cat="Binary") for p in range(n_persons)]
            for f in range(n_flights)]

    # Each flight has as many crew as it needs.
    for f in range(n_flights):
        problem += pulp.lpSum(crew[f]) == required_crew[f][0]

    # Each flight has at least the fewest people it needs with each attribute.
    for f in range(n_flights):
        for a in range(n_attributes):
            problem += pulp.lpSum(attributes[p][a] * crew[f][p]
                                  for p in range(n_persons)) >= required_crew[f][a + 1]

    # A person assigned to a flight has the next two flights off.
    for f in range(n_flights - 2):
        for p in range(n_persons):
            problem += crew[f][p] + crew[f + 1][p] + crew[f + 2][p] <= 1

    # works[p] is 1 when person p is assigned to at least one flight, and 0 when not
    works = [pulp.LpVariable(f"works{p}", cat="Binary") for p in range(n_persons)]
    # A person assigned to any flight is marked as working.
    for p in range(n_persons):
        for f in range(n_flights):
            problem += crew[f][p] <= works[p]
    # At least one person works.
    problem += pulp.lpSum(works) >= 1

    return problem, {"crew": crew}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
