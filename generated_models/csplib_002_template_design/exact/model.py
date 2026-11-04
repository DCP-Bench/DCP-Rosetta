# csplib_002_template_design: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_002_template_design.py csplib_002_template_design.json

from itertools import product

from exact import Exact


def create_model(instance):
    """Template design: a printer makes several variations of a carton on mother
    sheets, each printed from a template with a fixed number of slots holding one
    variation each. Choose what each template holds and how many sheets to print
    from it, so that every variation reaches its demand with as few sheets as possible."""
    n_slots = instance["n_slots"]          # the number of slots on a template
    n_templates = instance["n_templates"]  # the number of templates
    n_var = instance["n_var"]              # the number of variations
    demand = instance["demand"]            # demand[v]: the number of copies wanted of variation v

    # The most sheets printed from one template: the largest demand of any variation.
    ub = max(demand)
    # A template holds at most n_var copies of one variation, and at most n_slots.
    max_copies = min(n_var, n_slots)
    # The most copies of one variation that can be printed over all templates.
    max_printed = max_copies * n_templates * ub

    solver = Exact()

    # Exact identifies its variables by name.
    # production[t] is the number of sheets printed from template t, from 1 to ub.
    production = [f"production_{t}" for t in range(n_templates)]
    for name in production:
        solver.addVariable(name, 1, ub)

    # layout[t][v] is the number of slots of template t that hold variation v.
    layout = [[f"layout_{t}_{v}" for v in range(n_var)] for t in range(n_templates)]
    for t in range(n_templates):
        for v in range(n_var):
            solver.addVariable(layout[t][v], 0, max_copies)

    # All n_slots slots of each template are used.
    for t in range(n_templates):
        solver.addConstraint([(1, name) for name in layout[t]], True, n_slots, True, n_slots)

    # printed[v] is the number of copies of variation v printed over all templates, from its demand up to max_printed.
    printed = [f"printed_{v}" for v in range(n_var)]
    # vectors[k] is one possible list of copies of a variation, one entry per template.
    vectors = list(product(range(max_copies + 1), repeat=n_templates))
    # pick[v][k] is 1 when variation v takes vector k, and 0 when not.
    pick = [[f"pick_{v}_{k}" for k in range(len(vectors))] for v in range(n_var)]
    # Each variation first takes its whole list of copies over the templates. Once that list
    # is fixed, the copies printed of the variation are a sum over the templates.
    for v in range(n_var):
        solver.addVariable(printed[v], demand[v], max_printed)
        for name in pick[v]:
            solver.addVariable(name, 0, 1)

        # Each variation takes exactly one vector.
        solver.addConstraint([(1, name) for name in pick[v]], True, 1, True, 1)

        # The copies of variation v on template t are the t-th entry of the vector taken.
        for t in range(n_templates):
            solver.addConstraint([(c[t], pick[v][k]) for k, c in enumerate(vectors) if c[t]]
                                 + [(-1, layout[t][v])], True, 0, True, 0)

        # Every variation reaches its demand: when vector k is taken, the copies printed equal
        # the entries of the vector times the sheets of each template. Otherwise max_printed
        # is large enough to leave the pair of constraints slack.
        for k, c in enumerate(vectors):
            # dot holds the copies from vector k, each with its template's sheets, negated.
            dot = [(-c[t], production[t]) for t in range(n_templates) if c[t]]
            solver.addConstraint([(1, printed[v])] + dot + [(max_printed, pick[v][k])],
                                 False, 0, True, max_printed)
            solver.addConstraint([(1, printed[v])] + dot + [(-max_printed, pick[v][k])],
                                 True, -max_printed)

    # Every sheet gives n_slots copies, so the copies printed over all variations are n_slots
    # times the number of sheets.
    solver.addConstraint([(1, name) for name in printed] + [(-n_slots, name) for name in production],
                         True, 0, True, 0)
    # The sheets, with n_slots copies each, cover the total demand.
    solver.addConstraint([(n_slots, name) for name in production], True, sum(demand))

    # Minimise the number of sheets printed in total.
    solver.setObjective([(1, name) for name in production], minimize=True)

    return solver, {"production": production, "layout": layout}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
