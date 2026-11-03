# capital_budget: a SCIP (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python capital_budget.py capital_budget.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """A company chooses which investments to make. Each investment yields a
    net present value (NPV) and needs a cash outflow now, and the total outflow
    must stay within the budget. Choose the investments that maximise the total
    NPV.

    Returns the model and its outputs: x, one 0/1 entry per investment (1 when
    the investment is chosen), and z, the total NPV of the chosen investments.
    """
    budget = instance["budget"]        # the total cash available for investment
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow investment i needs now
    npv = instance["npv"]              # npv[i]: the net present value that investment i yields

    model = Model("capital_budget")

    # x[i] is 1 when investment i is chosen, and 0 when not
    x = [model.addVar(f"x_{i}", vtype="B") for i in range(len(npv))]

    # z is the total NPV of the chosen investments, the objective. Its bounds follow
    # from the NPVs alone: each x[i] is 0 or 1, so z is at least the sum of the
    # negative NPVs and at most the sum of the positive ones.
    z = model.addVar("z", vtype="I",
                     lb=sum(min(0, v) for v in npv),
                     ub=sum(max(0, v) for v in npv))

    # The cash outflows of the chosen investments add up to no more than the budget.
    model.addCons(quicksum(c * xi for c, xi in zip(cash_flow, x)) <= budget)

    # z is the total NPV of the chosen investments.
    model.addCons(z == quicksum(v * xi for v, xi in zip(npv, x)))

    # Maximise the total NPV of the chosen investments. The objective is held in the
    # bounded integer z, so the optimum can be pinned when all optimal choices are listed.
    model.setObjective(z, "maximize")

    return model, {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
