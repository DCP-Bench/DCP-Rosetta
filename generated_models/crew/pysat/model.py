# crew: a PySAT (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python crew.py crew.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a certain number of cabin
    crew, and they have to speak certain languages. Every cabin crew member has two
    flights off after an attended flight."""
    attributes = instance["attributes"]  # attributes[p]: which of the five skills attendant p has: steward, hostess, and speaking French, Spanish or German
    required = instance["required_crew"]  # required[f]: the size of the crew flight f needs, then the fewest crew with each skill
    n_persons = len(attributes)  # the number of attendants
    n_flights = len(required)  # the number of flights
    n_attributes = len(attributes[0])  # the number of skills

    pool = IDPool()
    # crew[f][p] is true when attendant p works on flight f.
    crew = [[pool.id(("crew", f, p)) for p in range(n_persons)] for f in range(n_flights)]

    formula = CNF()
    for f in range(n_flights):
        # Flight f has exactly as many crew as it needs.
        formula.extend(CardEnc.equals(lits=crew[f], bound=required[f][0], vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        # Among them, flight f has enough attendants with each skill.
        for a in range(n_attributes):
            # The attendants on flight f who have skill a.
            skilled = [crew[f][p] for p in range(n_persons) if attributes[p][a]]
            # A requirement of zero adds no constraint.
            if required[f][a + 1] > 0:
                formula.extend(CardEnc.atleast(lits=skilled, bound=required[f][a + 1], vpool=pool,
                                               encoding=EncType.seqcounter).clauses)

    # An attendant who works a flight has the next two flights off, so no attendant works
    # two of any three consecutive flights.
    for f in range(n_flights - 2):
        for p in range(n_persons):
            formula.append([-crew[f][p], -crew[f + 1][p]])
            formula.append([-crew[f][p], -crew[f + 2][p]])
            formula.append([-crew[f + 1][p], -crew[f + 2][p]])

    return formula, {"crew": crew}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
