# capital_budget: a CPLEX (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python capital_budget.py capital_budget.json

from docplex.mp.model import Model


def create_model(instance):
    """Capital budgeting: choose investments within the budget to maximise the total net present value."""
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow investment i requires now
    budget = instance["budget"]        # the total available for investment
    n_investments = len(npv)

    model = Model("capital_budget")

    # x[i] is 1 when investment i is chosen.
    x = model.binary_var_list(n_investments, name="x")

    # The cash outflow of the chosen investments stays within the budget.
    model.add_constraint(model.dot(x, cash_flow) <= budget, ctname="budget")

    # z is the total NPV of the chosen investments, and it is maximised.
    z = model.dot(x, npv)
    model.maximize(z)

    return model, {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
