# csplib_002_template_design: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_002_template_design.py csplib_002_template_design.json

import itertools

import mip

# Up to this many copy-count combinations for a variation, the layout is chosen over all
# templates at once, which bounds the sheets more tightly. Above it, template by template.
MAX_COMBINATIONS = 200


def combination_layout(model, production, n_slots, demand, templates, variations, max_demand):
    # layout[t][v] collects the copies of variation v on template t, over all combinations.
    layout = [[[] for _ in variations] for _ in templates]
    for v in variations:
        # One choice per combination of copy counts for variation v.
        choices = []
        # counted[t] collects the sheets of template t that count towards variation v.
        counted = [[] for _ in templates]
        for copies in itertools.product(range(n_slots + 1), repeat=len(templates)):
            # A variation with no copy on any template cannot meet a positive demand.
            if sum(copies) == 0:
                continue
            # pick is 1 when variation v has copies[t] copies on each template t.
            pick = model.add_var(f"pick_{v}_{'_'.join(map(str, copies))}", var_type=mip.BINARY)
            choices.append(pick)
            # The copies of variation v printed under this combination, over all templates.
            printed = []
            for t in templates:
                layout[t][v].append(copies[t] * pick)
                if copies[t] == 0:
                    continue
                # Sheets of template t counted for variation v. Zero unless the combination
                # is chosen, and never more than needed to meet the demand with copies[t] per sheet.
                max_sheets = min(max_demand, -(-demand[v] // copies[t]))
                counted_sheets = model.add_var(lb=0, ub=max_sheets)
                model += counted_sheets <= max_sheets * pick
                counted[t].append(counted_sheets)
                printed.append(copies[t] * counted_sheets)
            # Under the chosen combination, the copies printed of variation v meet its demand.
            model += mip.xsum(printed) >= demand[v] * pick
        # Variation v takes exactly one combination of copy counts.
        model += mip.xsum(choices) == 1
        # For each template, the sheets counted for the variations do not exceed the sheets it prints.
        for t in templates:
            model += mip.xsum(counted[t]) <= production[t]
    return [[mip.xsum(layout[t][v]) for v in variations] for t in templates]


def per_template_layout(model, production, n_slots, demand, templates, variations, max_demand):
    # has[t][v][k] is 1 when template t carries exactly k copies of variation v.
    has = [[[model.add_var(f"has_{t}_{v}_{k}", var_type=mip.BINARY) for k in range(n_slots + 1)]
            for v in variations] for t in templates]
    # sheets[t, v, k]: sheets of template t counted for variation v when it carries k copies
    # of it. Zero unless has[t][v][k] is 1, and never more than needed to meet the demand
    # with k copies per sheet.
    sheets = {}
    for t in templates:
        for v in variations:
            # Variation v has exactly one number of copies on template t.
            model += mip.xsum(has[t][v]) == 1
            for k in range(1, n_slots + 1):
                max_sheets = min(max_demand, -(-demand[v] // k))
                sheets[t, v, k] = model.add_var(lb=0, ub=max_sheets)
                model += sheets[t, v, k] <= max_sheets * has[t][v][k]
            # For each variation on template t, the sheets counted for it do not exceed the
            # sheets printed from t.
            model += mip.xsum(sheets[t, v, k] for k in range(1, n_slots + 1)) <= production[t]
    # Over all templates, the copies printed of each variation meet its demand.
    for v in variations:
        model += mip.xsum(k * sheets[t, v, k] for t in templates for k in range(1, n_slots + 1)) >= demand[v]
    # Implied: the copies counted from template t never exceed the copies its sheets carry.
    for t in templates:
        model += mip.xsum(k * sheets[t, v, k] for v in variations for k in range(1, n_slots + 1)) \
            <= n_slots * production[t]
    return [[mip.xsum(k * has[t][v][k] for k in range(n_slots + 1)) for v in variations] for t in templates]


def create_model(instance):
    """Template design: a printer makes several variations of a carton on mother sheets.
    Each sheet is printed from a template with a fixed number of slots, and each slot holds
    one copy of one variation. Choose what each template holds and how many sheets to print
    from it, so that every variation reaches its demand with as few sheets as possible."""
    n_slots = instance["n_slots"]          # slots on each template
    n_templates = instance["n_templates"]  # number of templates to design
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand[v]: copies of variation v to print

    templates = range(n_templates)
    variations = range(n_var)
    max_demand = max(demand)  # the largest demand of any variation

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # production[t]: sheets printed from template t, at least one and at most the largest demand.
    production = [model.add_var(f"production_{t}", lb=1, ub=max_demand, var_type=mip.INTEGER)
                  for t in templates]

    # Copies of each variation on each template, with the demand of every variation met.
    if (n_slots + 1) ** n_templates <= MAX_COMBINATIONS:
        layout = combination_layout(model, production, n_slots, demand, templates, variations, max_demand)
    else:
        layout = per_template_layout(model, production, n_slots, demand, templates, variations, max_demand)

    # Every slot of a template holds one variation.
    for t in templates:
        model += mip.xsum(layout[t][v] for v in variations) == n_slots

    # Implied: each sheet carries n_slots copies, so the sheets printed cover the total demand.
    # A number of sheets is whole, so round up.
    model += mip.xsum(production) >= -(-sum(demand) // n_slots)

    # The total number of sheets printed.
    model.objective = mip.xsum(production)

    return model, {"layout": layout, "production": production}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
