# capital_budget: a Python-MIP (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python capital_budget.py capital_budget.json

import mip


def create_model(instance):
    """A company considers a number of investments, each with a net present value (NPV) and a cash
    outflow now. Choose the investments that maximize the total NPV within the total budget."""
    budget = instance["budget"]        # the total budget available for investment
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow investment i requires now
    n = len(npv)                       # the number of investments
    total_npv = sum(npv)               # the NPV of all investments together

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # x[i] is 1 when investment i is chosen, and 0 when not
    x = [model.add_var(f"x_{i}", var_type=mip.BINARY) for i in range(n)]

    # z is the total NPV of the chosen investments
    z = model.add_var("z", lb=0, ub=total_npv, var_type=mip.INTEGER)

    # The cash outflow of the chosen investments stays within the budget.
    model += mip.xsum(cash_flow[i] * x[i] for i in range(n)) <= budget

    # The total NPV is the sum of the NPVs of the chosen investments.
    model += z == mip.xsum(npv[i] * x[i] for i in range(n))

    # Maximize the total NPV.
    model.objective = z

    return model, {"x": x, "z": z}


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
