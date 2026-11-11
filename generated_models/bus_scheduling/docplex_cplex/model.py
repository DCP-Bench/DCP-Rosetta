# bus_scheduling: a CPLEX (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python bus_scheduling.py bus_scheduling.json

from docplex.mp.model import Model


def create_model(instance):
    """Bus scheduling: the fewest buses that meet the demand in every 4-hour slot of the day."""
    demands = instance["demands"]  # demands[i]: buses needed in the i-th 4-hour slot
    slots = len(demands)

    model = Model("bus_scheduling")

    # x[i] is the number of buses that start working in slot i. Starting demands[i] buses in
    # every slot i already meets the demand, so no optimal plan starts more than sum(demands)
    # buses in one slot.
    x = model.integer_var_list(slots, 0, sum(demands), name="x")

    # A bus works 8 successive hours, so in slot i the buses on duty are those that start in slot
    # i and those that started in the slot before it (for slot 0 the last slot: the day is
    # cyclic, x[-1] is the last entry); they meet the demand of slot i.
    model.add_constraints(x[i - 1] + x[i] >= demands[i] for i in range(slots))

    # Use as few buses as possible.
    model.minimize(model.sum(x))

    return model, {"x": x}


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
