# capital_budget: a CPMpy model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python capital_budget.py capital_budget.json

import cpmpy as cp


def create_model(instance):
    """A company considers a number of investments, each with a net present value (NPV) and a cash
    outflow now. Choose the investments that maximise the total NPV within the total budget."""
    budget = instance["budget"]          # the total budget available for investment
    npv = instance["npv"]                # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]    # cash_flow[i]: the cash outflow investment i requires now

    # x[i] is true when investment i is chosen
    x = cp.boolvar(shape=len(npv), name="x")
    # z is the total NPV of the chosen investments; it cannot exceed the NPV of all investments.
    z = cp.intvar(0, sum(npv), name="z")

    model = cp.Model()
    # The cash outflow of the chosen investments stays within the budget.
    model.add(cp.sum(x * cash_flow) <= budget)
    # The total NPV is the sum of the NPVs of the chosen investments.
    model.add(z == cp.sum(x * npv))

    # Maximise the total NPV.
    model.maximize(z)

    return model, {"z": z, "x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
