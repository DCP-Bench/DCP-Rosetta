# crew: a Z3 (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python crew.py crew.json

import z3


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a certain number of cabin
    crew, and they have to speak certain languages. Every cabin crew member has two
    flights off after an attended flight."""
    # attributes[p]: whether attendant p is a steward, a hostess, and speaks French, Spanish
    # and German (1 for yes, 0 for no)
    attributes = instance["attributes"]
    # required_crew[f]: the crew size of flight f, then the fewest stewards, hostesses, and
    # French, Spanish and German speakers that flight needs among its crew
    required_crew = instance["required_crew"]
    n_persons = len(attributes)  # the number of attendants
    n_flights = len(required_crew)  # the number of flights
    n_skills = len(attributes[0])  # the number of skills listed for each attendant

    # crew[f][p] is true when attendant p works flight f
    crew = [[z3.Bool(f"crew_{f}_{p}") for p in range(n_persons)] for f in range(n_flights)]
    # num_working is the number of attendants who work at least one flight
    num_working = z3.Int("num_working")

    solver = z3.Solver()

    # At least one attendant works, and at most all of them do.
    solver.add(
        num_working >= 1,
        num_working <= n_persons,
        num_working == z3.Sum([z3.If(z3.Or([crew[f][p] for f in range(n_flights)]), 1, 0)
                           for p in range(n_persons)]),
    )

    for f in range(n_flights):
        # Each flight has exactly the crew size it requires.
        solver.add(z3.PbEq([(crew[f][p], 1) for p in range(n_persons)], required_crew[f][0]))

        # Each flight has at least the required number of stewards, hostesses, and French,
        # Spanish and German speakers among its crew.
        for j in range(n_skills):
            skilled = [(crew[f][p], attributes[p][j]) for p in range(n_persons) if attributes[p][j] > 0]
            solver.add(z3.PbGe(skilled, required_crew[f][j + 1]))

    # After a flight, a crew member has the next two flights off, so works at most one
    # flight in any three consecutive flights.
    for f in range(n_flights - 2):
        for p in range(n_persons):
            solver.add(z3.AtMost(crew[f][p], crew[f + 1][p], crew[f + 2][p], 1))

    return solver, {"crew": crew}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
