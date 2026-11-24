# capital_budget: a PyCSP3 model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python capital_budget.py capital_budget.json

from pycsp3 import *


def create_model(instance):
    """A company considers a number of investments. Each investment has a net present
    value (NPV) and a cash outflow now. The cash outflows must fit within the budget.
    Choose the investments that maximise the total NPV."""
    budget = instance["budget"]        # the total money available for investment now
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow of investment i
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    n_investments = len(npv)

    # x[i] is 1 when investment i is chosen, 0 otherwise
    x = VarArray(size=n_investments, dom={0, 1})

    # z: the total NPV of the chosen investments; no investment set can exceed the sum of all NPVs
    z = Var(dom=range(sum(npv) + 1))

    satisfy(
        # The cash outflows of the chosen investments add up to no more than the budget.
        Sum(cash_flow[i] * x[i] for i in range(n_investments)) <= budget,
        # The total NPV is the sum of the NPVs of the chosen investments.
        z == Sum(npv[i] * x[i] for i in range(n_investments)),
    )

    # Maximise the total NPV.
    maximize(z)

    return {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("x =", values(outputs["x"]))
        print("z =", value(outputs["z"]))
    else:
        print("No solution:", status())
