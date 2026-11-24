# csplib_002_template_design: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_002_template_design.py csplib_002_template_design.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Template design: choose which variations, and how many copies of each, go on each printing template, and how many sheets to print from each template, so that every variation's demand is met with the fewest printed sheets."""
    n_slots = instance["n_slots"]          # the number of items that fit on one mother sheet
    n_templates = instance["n_templates"]  # the number of templates; the instance fixes it
    n_var = instance["n_var"]              # the number of design variations
    demand = instance["demand"]            # demand[v]: the number of copies of variation v ordered
    templates = range(n_templates)
    variations = range(n_var)
    # copies: the possible numbers of copies of a variation on one template, 0 up to all n_slots slots.
    copies = range(n_slots + 1)
    # ub bounds the sheets printed from one template. Not in the statement, but it cannot cut off
    # a solution: a template printing more sheets than the largest demand already covers every
    # variation on it, so fewer sheets would meet the demand too.
    ub = max(demand)

    model = gp.Model("template_design")

    # production[i] is the number of sheets printed from template i. The lower bound 1 is not
    # in the statement: a template printed no sheets would not be used.
    production = model.addVars(templates, lb=1, ub=ub, vtype=GRB.INTEGER, name="production")

    # has[i, v, c] is 1 when template i carries c copies of variation v.
    has = model.addVars(templates, variations, copies, vtype=GRB.BINARY, name="has")
    # Each variation has exactly one copy count on each template.
    model.addConstrs((has.sum(i, v, "*") == 1 for i in templates for v in variations), name="one_count")
    # layout[i][v] is the number of copies of variation v on template i.
    layout = [[gp.quicksum(c * has[i, v, c] for c in copies) for v in variations] for i in templates]

    # sheets[i, v, c] is the number of sheets printed from template i that carry c copies of
    # variation v. Splitting production[i] this way keeps the model free of products of two
    # variables. This is an encoding of the statement, not a rule in it.
    sheets = model.addVars(templates, variations, copies, lb=0, ub=ub, vtype=GRB.CONTINUOUS, name="sheets")
    # The sheets for a variation on a template add up to that template's production (encoding).
    model.addConstrs((sheets.sum(i, v, "*") == production[i] for i in templates for v in variations),
                     name="split")
    # Sheets count only under the copy count the template really carries (encoding).
    model.addConstrs((sheets[i, v, c] <= ub * has[i, v, c]
                      for i in templates for v in variations for c in copies), name="only_if")

    # Every slot of every template is filled: the copies on a template add up to n_slots.
    model.addConstrs((gp.quicksum(layout[i][v] for v in variations) == n_slots for i in templates),
                     name="slots")
    # Redundant, not in the statement: the same fact counted over the printed sheets. It is
    # implied by the rules above and is added to tighten the model.
    model.addConstrs((gp.quicksum(c * sheets[i, v, c] for v in variations for c in copies)
                      == n_slots * production[i] for i in templates), name="slots_per_sheet")

    # Demand: the copies printed of each variation, sheets times copies per sheet summed over
    # the templates, reach its demand.
    model.addConstrs((gp.quicksum(c * sheets[i, v, c] for i in templates for c in copies) >= demand[v]
                      for v in variations), name="demand")
    # Redundant, not in the statement: the sheets cover the total demand, since every template
    # fills all its slots. Implied by the rules above and added to tighten the model.
    model.addConstr(n_slots * production.sum() >= sum(demand), name="total_demand")

    # Minimise the total number of sheets printed, summed over the templates.
    model.setObjective(production.sum(), GRB.MINIMIZE)

    return model, {
        "production": [production[i] for i in templates],  # production[i]: sheets printed from template i
        "layout": layout,  # layout[i][v]: copies of variation v on template i
    }


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
