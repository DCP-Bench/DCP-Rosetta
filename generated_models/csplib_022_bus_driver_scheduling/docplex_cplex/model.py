# csplib_022_bus_driver_scheduling: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from docplex.mp.model import Model


def create_model(instance):
    """Bus driver scheduling: choose a set of shifts so that every piece of work is covered by
    exactly one chosen shift, using as few shifts as possible (set partitioning)."""
    num_work = instance["num_work"]      # number of pieces of work
    num_shifts = instance["num_shifts"]  # number of possible shifts
    shifts = instance["shifts"]          # shifts[i] lists the pieces of work shift i covers

    model = Model("bus_driver_scheduling")

    # x[i] is 1 if shift i is selected.
    x = model.binary_var_list(num_shifts, name="x")

    # Each piece of work is covered by exactly one selected shift.
    model.add_constraints(model.sum(x[i] for i in range(num_shifts) if t in shifts[i]) == 1
                          for t in range(num_work))

    # Use as few shifts as possible.
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
