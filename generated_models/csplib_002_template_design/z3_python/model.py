# csplib_002_template_design: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_002_template_design.py csplib_002_template_design.json

import z3


def create_model(instance):
    """Template design: a printer makes several variations of a carton on mother
    sheets, each printed from a template with a fixed number of slots holding one
    variation each. Choose what each template holds and how many sheets to print
    from it, so that every variation reaches its demand with as few sheets as possible."""
    n_slots = instance["n_slots"]          # number of slots on a template
    n_templates = instance["n_templates"]  # number of different templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand[v]: copies wanted of variation v
    max_sheets = max(demand)               # one sheet gives at least one copy of a variation it carries

    # production[t] is the number of sheets printed from template t.
    production = [z3.Int(f"production_{t}") for t in range(n_templates)]

    # layout[t][v] is the number of slots of template t that hold variation v.
    layout = [[z3.Int(f"layout_{t}_{v}") for v in range(n_var)] for t in range(n_templates)]

    # printed[v] is the number of copies of variation v printed over all the sheets.
    printed = [z3.Int(f"printed_{v}") for v in range(n_var)]

    # total_sheets is the number of sheets printed from all the templates.
    total_sheets = z3.Sum(production)

    solver = z3.Optimize()

    # Each template is printed at least once, and no more often than max_sheets.
    for t in range(n_templates):
        solver.add(production[t] >= 1, production[t] <= max_sheets)

    # A variation takes at most n_var slots of one template.
    for t in range(n_templates):
        solver.add([layout[t][v] >= 0 for v in range(n_var)])
        solver.add([layout[t][v] <= n_var for v in range(n_var)])

    # Every slot of every template holds a variation.
    for t in range(n_templates):
        solver.add(z3.Sum(layout[t]) == n_slots)

    # Copies of variation v printed: for each template, the sheets printed from it times the
    # slots holding v on it. A product of two variables is slow to solve, so the product is
    # written as a sum over the possible slot counts k, each adding k times the sheets.
    for v in range(n_var):
        solver.add(printed[v] == z3.Sum([z3.If(layout[t][v] == k, k * production[t], 0)
                                         for t in range(n_templates)
                                         for k in range(1, n_var + 1)]))

    # Every variation reaches its demand.
    for v in range(n_var):
        solver.add(printed[v] >= demand[v])

    # Every sheet carries n_slots copies, so the copies printed in total are n_slots times the
    # sheets. The sheets must also cover the total demand.
    solver.add(z3.Sum(printed) == n_slots * total_sheets)
    solver.add(n_slots * total_sheets >= sum(demand))

    # Print as few sheets as possible.
    solver.minimize(total_sheets)

    return solver, {"production": production, "layout": layout}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
