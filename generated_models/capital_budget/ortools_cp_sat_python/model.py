# capital_budget: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install ortools`):
#   python capital_budget.py capital_budget.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A company chooses investments, each with a net present value (NPV) and a cash outflow now.
    Choose the investments that maximize the total NPV, with the cash outflow of the chosen
    investments within the total budget."""
    budget = instance["budget"]        # the total budget available for investment
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow investment i requires now

    model = cp_model.CpModel()

    # x[i] is true when investment i is chosen
    x = [model.new_bool_var(f"x_{i}") for i in range(len(npv))]
    # z is the total NPV
    z = model.new_int_var(0, sum(npv), "z")

    # The cash outflow of the chosen investments stays within the budget.
    model.add(sum(c * xi for c, xi in zip(cash_flow, x)) <= budget)
    # The total NPV is the sum of the NPVs of the chosen investments.
    model.add(z == sum(v * xi for v, xi in zip(npv, x)))

    # Maximize the total NPV.
    model.maximize(z)

    return model, {"z": z, "x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
