# csplib_002_template_design: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_002_template_design.py csplib_002_template_design.json

from pyscipopt import Model


def create_model(instance):
    """Template design for a colour printing firm.

    Each mother sheet is printed from a template: a thin aluminium sheet with the
    designs of several product variations (for example cat-food cartons) etched on it.
    The firm produces n_templates templates, each with n_slots positions, and each
    position carries one copy of one variation. Printing a template once gives as many
    copies of each variation as it has positions for it. Choose the variations on each template and how many sheets to print from
    each template, so that every variation gets at least its demand, with as few printed
    sheets as possible.
    """
    n_slots = instance["n_slots"]          # positions on one template
    n_templates = instance["n_templates"]  # number of templates the firm produces
    n_var = instance["n_var"]              # number of product variations
    demand = instance["demand"]            # demand[j]: copies of variation j to be printed

    model = Model("csplib_002_template_design")

    # layout[i, j]: number of positions of template i that carry variation j. A variation
    # can take every position of a template, which is the bound n_slots from the data.
    layout = model.addMatrixVar((n_templates, n_var), vtype="I", lb=0, ub=n_slots)

    # production[i]: number of sheets printed from template i. The statement gives
    # each template between 1 sheet (lb=1) and max(demand) sheets. The upper bound is also derived: a
    # template printed more than max(demand) times can print max(demand) times instead,
    # since each variation it carries still gets at least max(demand) >= demand copies
    # from it, so no optimal solution is cut off.
    production = model.addMatrixVar((n_templates,), vtype="I", lb=1, ub=max(demand))

    # Every position of a template is filled: the variations on a template add up to
    # n_slots.
    model.addMatrixCons(layout.sum(axis=1) == n_slots)

    # Copies of variation j printed: the sheets printed from each template times the copies
    # of j on that template, summed over templates, is at least the demand of j. The product
    # of two integer variables is nonlinear; SCIP handles it directly in a constraint, so no
    # auxiliary variable is needed.
    printed = production.reshape((n_templates, 1)) * layout
    model.addMatrixCons(printed.sum(axis=0) >= demand)

    # Minimise the total number of printed sheets.
    model.setObjective(production.sum(), "minimize")

    return model, {"layout": layout, "production": production}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
