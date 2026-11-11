# csplib_002_template_design: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_002_template_design.py csplib_002_template_design.json

from pycsp3 import *


def create_model(instance):
    """A colour printing firm prints several variations of a design from templates, each
    template an aluminium sheet with a fixed number of slots. Decide which variations, and
    how many copies of each, to etch on each template, and how many sheets to print from
    each template. Every slot of a template is filled. Each template prints between 1 sheet
    and as many sheets as the largest demand. The sheets printed must meet the demand of
    every variation. Minimise the total number of printed sheets."""
    n_templates = instance["n_templates"]  # the number of templates
    n_slots = instance["n_slots"]          # the number of slots on each template
    n_var = instance["n_var"]              # the number of design variations
    demand = instance["demand"]            # demand[v] is the number of copies of variation v to print
    max_sheets = max(demand)               # the most sheets a template prints, the largest demand (the description's bound)

    # layout[t][v] is the number of slots of template t that carry variation v; at most all n_slots.
    layout = VarArray(size=[n_templates, n_var], dom=range(n_slots + 1))

    # production[t] is the number of sheets printed from template t, between 1 and max_sheets.
    production = VarArray(size=n_templates, dom=range(1, max_sheets + 1))

    # Every slot of template t is filled.
    satisfy(Sum(layout[t]) == n_slots for t in range(n_templates))

    # The sheets printed from the templates meet the demand of each variation.
    satisfy(
        Sum(production[t] * layout[t][v] for t in range(n_templates)) >= demand[v]
        for v in range(n_var)
    )

    # Redundant bound, implied by the two constraints above: every sheet carries n_slots copies, so the
    # sheets printed must total at least sum(demand) / n_slots. Derived by us, not stated in the
    # description; it only tightens the search for the minimum.
    total_demand = sum(demand)
    satisfy(Sum(production) * n_slots >= total_demand)

    # Minimise the total number of printed sheets.
    minimize(Sum(production))

    return {"layout": layout, "production": production}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("layout", "=")
        for row in outputs["layout"]:
            print(values(row))
    else:
        print("No solution:", status())
