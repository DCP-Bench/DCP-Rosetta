# csplib_002_template_design: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_002_template_design.py csplib_002_template_design.json

import pulp


def create_model(instance):
    """Template design: a printer makes several variations of a carton on mother
    sheets, each printed from a template with a fixed number of slots holding one
    variation each. Choose what each template holds and how many sheets to print
    from it, so that every variation reaches its demand with as few sheets as possible."""
    n_slots = instance["n_slots"]          # number of slots on a template
    n_templates = instance["n_templates"]  # number of different templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand[v]: copies wanted of variation v

    # No template is printed more often than the largest demand, since each sheet gives
    # at least one copy of some variation.
    max_sheets = max(demand)

    # A variation takes at most n_var slots on a template, and never more than the template has.
    max_slots_per_variation = min(n_var, n_slots)

    problem = pulp.LpProblem("template_design", pulp.LpMinimize)

    # production[t] is the number of sheets printed from template t, at least one
    production = [pulp.LpVariable(f"production_{t}", 1, max_sheets, cat="Integer")
                  for t in range(n_templates)]

    # layout[t][v] is the number of slots of template t that hold variation v
    layout = [[pulp.LpVariable(f"layout_{t}_{v}", 0, max_slots_per_variation, cat="Integer")
               for v in range(n_var)]
              for t in range(n_templates)]

    # has[t][v][k] is 1 when template t holds exactly k slots of variation v, and 0 otherwise
    has = pulp.LpVariable.dicts(
        "has", (range(n_templates), range(n_var), range(max_slots_per_variation + 1)),
        cat="Binary")

    # sheets[t][v][k] is the number of sheets printed from template t, counted only when
    # template t holds k slots of variation v
    sheets = pulp.LpVariable.dicts(
        "sheets", (range(n_templates), range(n_var), range(max_slots_per_variation + 1)),
        0, max_sheets)

    # Every slot of every template holds a variation.
    for t in range(n_templates):
        problem += pulp.lpSum(layout[t]) == n_slots

    for t in range(n_templates):
        for v in range(n_var):
            # Template t holds one definite number of slots of variation v.
            problem += pulp.lpSum(has[t][v][k] for k in range(max_slots_per_variation + 1)) == 1
            problem += layout[t][v] == pulp.lpSum(
                k * has[t][v][k] for k in range(max_slots_per_variation + 1))

            # Every sheet printed from template t is counted under the slots it holds for v.
            problem += pulp.lpSum(sheets[t][v][k] for k in range(max_slots_per_variation + 1)) \
                == production[t]
            for k in range(max_slots_per_variation + 1):
                problem += sheets[t][v][k] <= max_sheets * has[t][v][k]

    # Every sheet from template t gives n_slots copies, so the copies from template t add up
    # to n_slots times the sheets printed from it.
    for t in range(n_templates):
        problem += pulp.lpSum(k * sheets[t][v][k] for v in range(n_var)
                              for k in range(max_slots_per_variation + 1)) \
            == n_slots * production[t]

    # Every variation gets at least its demand in copies, over all templates.
    for v in range(n_var):
        problem += pulp.lpSum(k * sheets[t][v][k]
                              for t in range(n_templates)
                              for k in range(max_slots_per_variation + 1)) >= demand[v]

    # The printed sheets give n_slots copies each, which must cover the total demand.
    problem += n_slots * pulp.lpSum(production) >= sum(demand)

    # Print as few sheets as possible.
    problem += pulp.lpSum(production)

    return problem, {"production": production, "layout": layout}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
