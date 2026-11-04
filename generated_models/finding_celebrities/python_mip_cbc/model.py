# finding_celebrities: a Python-MIP (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python finding_celebrities.py finding_celebrities.json

import mip


def create_model(instance):
    """At a party, a celebrity is a person that everybody knows but who knows
    only other celebrities. Find the celebrities; at least one is present."""
    graph = instance["graph"]  # graph[i][j]: 1 when person i knows person j, 0 when not
    n_people = len(graph)      # the number of people at the party

    model = mip.Model(solver_name="CBC")

    # celebrity[i] is 1 when person i is a celebrity, and 0 when not.
    celebrity = []
    for i in range(n_people):
        # Everybody else knows person i. Otherwise person i cannot be a celebrity, so the value is fixed to 0.
        known_by_all = all(graph[j][i] == 1 for j in range(n_people) if j != i)
        celebrity.append(model.add_var(f"celebrity_{i}", lb=0, ub=int(known_by_all), var_type=mip.INTEGER))

    # At least one celebrity is present at the party.
    model += mip.xsum(celebrity) >= 1

    # A celebrity knows only celebrities: when person i knows person j and i is a celebrity, j is one too.
    for i in range(n_people):
        for j in range(n_people):
            if j != i and graph[i][j] == 1:
                model += celebrity[i] <= celebrity[j]

    return model, {"celebrities": celebrity}


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
