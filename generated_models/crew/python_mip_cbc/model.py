# crew: a Python-MIP (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python crew.py crew.json

import mip


def create_model(instance):
    """Assign flight attendants to flights. Each flight needs a certain number of cabin
    crew, and they have to speak certain languages. Every cabin crew member has two
    flights off after an attended flight."""
    # attributes[p]: the roles and languages of cabin crew member p: steward, hostess,
    # French, Spanish and German.
    attributes = instance["attributes"]
    # required_crew[f]: the crew size of flight f, then the fewest stewards, hostesses,
    # French, Spanish and German speakers it needs.
    required_crew = instance["required_crew"]
    n_people = len(attributes)  # the number of cabin crew members
    n_flights = len(required_crew)  # the number of flights

    model = mip.Model(solver_name="CBC")

    # crew[f][p] is 1 when cabin crew member p is assigned to flight f, and 0 when not.
    crew = [[model.add_var(f"crew_{f}_{p}", var_type=mip.BINARY) for p in range(n_people)]
            for f in range(n_flights)]

    # Each flight takes exactly the crew size it needs.
    for f in range(n_flights):
        model += mip.xsum(crew[f][p] for p in range(n_people)) == required_crew[f][0]

    # Each flight has enough stewards, hostesses and speakers of each language.
    for f in range(n_flights):
        for k in range(1, 6):
            # the crew members with this role or language
            members = [p for p in range(n_people) if attributes[p][k - 1] == 1]
            model += mip.xsum(crew[f][p] for p in members) >= required_crew[f][k]

    # A crew member who flies a flight does not fly either of the next two flights.
    for p in range(n_people):
        for f in range(n_flights):
            for g in (f + 1, f + 2):
                if g < n_flights:
                    model += crew[f][p] + crew[g][p] <= 1

    return model, {"crew": crew}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
