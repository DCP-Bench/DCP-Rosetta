# session3_kidney_exchange: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

import mip


def create_model(instance):
    """People on a waiting list for a kidney can donate one to some of the others,
    as given by a list of compatible recipients. Maximize the number of people who
    receive a kidney: anyone who gives a kidney must receive one, and nobody
    receives more than one."""
    n_people = instance["num_people"]    # the number of people on the waiting list
    compatible = instance["compatible"]  # compatible[i]: the people that person i can donate a kidney to

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # donates[(i, j)] is 1 when person i donates a kidney to person j, and 0 when not.
    # There is one such variable for each compatible pair of different people.
    donates = {}
    for i in range(n_people):
        for j1 in compatible[i]:
            j = j1 - 1
            if j != i:
                donates[(i, j)] = model.add_var(f"donates_{i}_{j}", var_type=mip.BINARY)

    # donations_from[i] are the donation variables of the donations person i makes.
    donations_from = [[donates[(i, j)] for j in range(n_people) if (i, j) in donates]
                      for i in range(n_people)]
    # donations_to[j] are the donation variables of the donations person j receives.
    donations_to = [[donates[(i, j)] for i in range(n_people) if (i, j) in donates]
                    for j in range(n_people)]

    # Each person donates at most one kidney.
    for i in range(n_people):
        if donations_from[i]:
            model.add_constr(mip.xsum(donations_from[i]) <= 1)

    # Each person receives at most one kidney.
    for j in range(n_people):
        if donations_to[j]:
            model.add_constr(mip.xsum(donations_to[j]) <= 1)

    # A person who donates a kidney also receives one.
    for i in range(n_people):
        if donations_from[i]:
            model.add_constr(mip.xsum(donations_from[i]) <= mip.xsum(donations_to[i]))

    # Maximize the number of kidney donations, which is the number of people receiving one.
    model.objective = mip.xsum(donates.values())

    # transplants[i][j] is the donation from person i to person j, or an empty expression (value 0) when that donation is not possible.
    transplants = [[donates[(i, j)] if (i, j) in donates else mip.LinExpr() for j in range(n_people)]
                   for i in range(n_people)]

    return model, {"transplants": transplants}


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
