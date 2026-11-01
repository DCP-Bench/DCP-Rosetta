# csplib_002_template_design: a CPMpy model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_002_template_design.py csplib_002_template_design.json

import cpmpy as cp


def create_model(instance):
    """Template design: a printer makes several variations of a carton on mother
    sheets, each printed from a template with a fixed number of slots holding one
    variation each. Choose what each template holds and how many sheets to print
    from it, so that every variation reaches its demand with as few sheets as possible."""
    n_slots = instance["n_slots"]          # number of slots on a template
    n_templates = instance["n_templates"]  # number of different templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand[v]: copies wanted of variation v

    # production[t] is the number of sheets printed from template t. Each template is
    # printed at least once, and never more often than the largest demand, since one
    # sheet gives at least one copy of a variation it carries.
    production = cp.intvar(1, max(demand), shape=n_templates, name="production")

    # layout[t, v] is the number of slots of template t that hold variation v
    layout = cp.intvar(0, n_slots, shape=(n_templates, n_var), name="layout")

    model = cp.Model()

    # Every slot of every template holds a variation.
    for t in range(n_templates):
        model.add(cp.sum(layout[t, :]) == n_slots)

    # Every variation reaches its demand over all printed sheets.
    for v in range(n_var):
        model.add(cp.sum(production * layout[:, v]) >= demand[v])

    # Implied constraint: all slots are filled, so every sheet gives n_slots copies and
    # together the sheets cover the total demand. It helps the solver bound the objective.
    model.add(n_slots * cp.sum(production) >= sum(demand))

    # Print as few sheets as possible.
    model.minimize(cp.sum(production))

    return model, {"layout": layout, "production": production}


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
