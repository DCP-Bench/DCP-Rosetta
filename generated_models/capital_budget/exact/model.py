# capital_budget: an Exact (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python capital_budget.py capital_budget.json

from exact import Exact


def create_model(instance):
    """A company chooses which investments to make. Each investment has a net present value
    and a cash outflow now. The total cash outflow must stay within the budget. Choose the
    investments that give the most total net present value."""
    npv = instance["npv"]                # npv[j]: the net present value of investment j
    cash_flow = instance["cash_flow"]    # cash_flow[j]: the cash outflow now for investment j
    budget = instance["budget"]          # the total cash available for investment
    n_investments = len(npv)

    solver = Exact()

    # Exact identifies its variables by name.
    # x[j] is 1 when investment j is chosen, and 0 when not
    x = [f"x{j}" for j in range(n_investments)]
    for name in x:
        solver.addVariable(name, 0, 1)

    # The cash outflow of the chosen investments stays within the budget.
    solver.addConstraint(list(zip(cash_flow, x)), False, 0, True, budget)

    # z is the total net present value of the chosen investments
    solver.addVariable("z", 0, sum(npv))
    solver.addConstraint(list(zip(npv, x)) + [(-1, "z")], True, 0, True, 0)

    # Choose the investments with the most total net present value.
    solver.setObjective([(1, "z")], minimize=False)

    return solver, {"x": x, "z": "z"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
