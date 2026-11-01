# csplib_002_template_design: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_002_template_design.py csplib_002_template_design.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Template design: a printer makes several variations of a carton on mother
    sheets, each printed from a template with a fixed number of slots holding one
    variation each. Choose what each template holds and how many sheets to print
    from it, so that every variation reaches its demand with as few sheets as possible."""
    n_slots = instance["n_slots"]          # number of slots on a template
    n_templates = instance["n_templates"]  # number of different templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand[v]: copies wanted of variation v

    model = cp_model.CpModel()

    # production[t] is the number of sheets printed from template t.
    production = [model.new_int_var(1, max(demand), f"production_{t}") for t in range(n_templates)]

    # layout[t][v] is the number of slots of template t that hold variation v
    layout = [[model.new_int_var(0, n_slots, f"layout_{t}_{v}") for v in range(n_var)]
              for t in range(n_templates)]

    # printed[t][v] is the number of copies of variation v printed from template t.
    printed = [[model.new_int_var(0, max(demand) * n_slots, f"printed_{t}_{v}")
                for v in range(n_var)]
               for t in range(n_templates)]
    for t in range(n_templates):
        for v in range(n_var):
            model.add_multiplication_equality(printed[t][v], [production[t], layout[t][v]])

    # Every slot of every template holds a variation.
    for t in range(n_templates):
        model.add(sum(layout[t]) == n_slots)

    # Every variation reaches its demand over all printed sheets.
    for v in range(n_var):
        model.add(sum(printed[t][v] for t in range(n_templates)) >= demand[v])

    # The printed sheets give n_slots copies each, which must cover the total demand.
    model.add(n_slots * sum(production) >= sum(demand))

    # The objective is the number of printed sheets.
    model.minimize(sum(production))

    return model, {"layout": layout, "production": production}


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
