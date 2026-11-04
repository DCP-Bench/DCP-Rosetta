# capital_budget: a PuLP (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python capital_budget.py capital_budget.json

import pulp


def create_model(instance):
    """A company considers a number of investments. Each has a net present value (NPV) and a cash
    outflow now. Choose the investments that maximize the total NPV without the cash outflow
    going over the budget."""
    budget = instance["budget"]        # the total cash available for investment now
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow investment i needs now

    problem = pulp.LpProblem("capital_budget", pulp.LpMaximize)

    # x[i] is 1 when investment i is chosen, and 0 when not
    chosen = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(npv))]
    # total is the NPV of the chosen investments, at most the NPV of all of them
    total = pulp.LpVariable("z", 0, sum(npv), cat="Integer")

    # The cash outflow of the chosen investments stays within the budget.
    problem += pulp.lpSum(c * x for c, x in zip(cash_flow, chosen)) <= budget

    # The total NPV is the sum of the NPVs of the chosen investments.
    problem += total == pulp.lpSum(v * x for v, x in zip(npv, chosen))

    # Maximize the total NPV.
    problem += total

    return problem, {"z": total, "x": chosen}


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
