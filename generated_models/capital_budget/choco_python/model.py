# capital_budget: a Choco-solver (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python capital_budget.py capital_budget.json

from pychoco.model import Model


def create_model(instance):
    """A company is considering a number of investments. Each one yields a net present value
    and needs a cash outflow now. Choose investments whose cash outflows fit within the
    budget."""
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow now for investment i
    budget = instance["budget"]        # the total cash available for investment
    n_investments = len(npv)           # the number of investments

    model = Model()

    # x[i] is true when investment i is chosen.
    x = [model.boolvar(name=f"x{i}") for i in range(n_investments)]

    # The chosen investments need no more cash than the budget.
    model.scalar(x, cash_flow, "<=", budget).post()

    # The total net present value of the chosen investments.
    total_npv = model.intvar(0, sum(npv), name="z")
    model.scalar(x, npv, "=", total_npv).post()

    # The objective is the total net present value, as large as possible.
    return model, {"z": total_npv, "x": x}, {"objective": total_npv, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
