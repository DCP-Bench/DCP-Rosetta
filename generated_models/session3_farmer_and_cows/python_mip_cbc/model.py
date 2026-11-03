# session3_farmer_and_cows: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

import mip


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and each cow gives
    as much milk as its number. He gives each of his sons a set number of cows,
    so that every son gets the same total amount of milk."""
    num_cows = instance["num_cows"]          # the number of cows
    num_sons = instance["num_sons"]          # the number of sons
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s receives

    model = mip.Model(solver_name="CBC")

    # gets[c][s] is 1 when son s receives cow c + 1, and 0 when not
    gets = [[model.add_var(f"gets_{c}_{s}", var_type=mip.BINARY) for s in range(num_sons)]
            for c in range(num_cows)]

    # Each cow goes to exactly one son.
    for c in range(num_cows):
        model.add_constr(mip.xsum(gets[c][s] for s in range(num_sons)) == 1)

    # Each son receives the number of cows given for him.
    for s in range(num_sons):
        model.add_constr(mip.xsum(gets[c][s] for c in range(num_cows)) == cows_per_son[s])

    # milk[s] is the total milk from the cows of son s.
    milk = [mip.xsum((c + 1) * gets[c][s] for c in range(num_cows)) for s in range(num_sons)]

    # Every son gets as much milk as son 0.
    for s in range(1, num_sons):
        model.add_constr(milk[s] == milk[0])

    # son_c is the son who receives cow c + 1.
    cow_assignments = []
    for c in range(num_cows):
        son = model.add_var(f"son_{c}", lb=0, ub=num_sons - 1, var_type=mip.INTEGER)
        model.add_constr(son == mip.xsum(s * gets[c][s] for s in range(num_sons)))
        cow_assignments.append(son)

    return model, {"cow_assignments": cow_assignments}


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
