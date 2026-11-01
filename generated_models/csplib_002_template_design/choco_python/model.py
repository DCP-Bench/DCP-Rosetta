# csplib_002_template_design: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_002_template_design.py csplib_002_template_design.json

from pychoco.model import Model


def create_model(instance):
    """Template design: a printing firm makes several variations of a carton on mother
    sheets. Each sheet is printed from a template with a fixed number of slots, and each
    slot holds one variation. Choose the templates and how many sheets to print from
    each, so that every variation gets its demanded copies from as few sheets as possible."""
    n_slots = instance["n_slots"]          # slots on each template, one copy per slot
    n_templates = instance["n_templates"]  # number of different templates
    n_var = instance["n_var"]              # number of variations of the product
    demand = instance["demand"]            # demand[v]: copies wanted of variation v

    # The largest demand, which bounds how often any template is printed.
    ub = max(demand)

    model = Model()

    # production[t] is the number of sheets printed from template t. Each template is printed at least once.
    production = [model.intvar(1, ub, name=f"production_{t}") for t in range(n_templates)]
    # layout[t][v] is the number of slots of template t that hold variation v.
    layout = [[model.intvar(0, n_var, name=f"layout_{t}_{v}") for v in range(n_var)]
              for t in range(n_templates)]

    # Every slot of every template holds a variation.
    for t in range(n_templates):
        model.sum(layout[t], "=", n_slots).post()

    # printed[t][v] is the number of copies of variation v printed from template t: the
    # sheets printed from t times the slots of t that hold v.
    printed = [[model.intvar(0, ub * n_var, name=f"printed_{t}_{v}") for v in range(n_var)]
               for t in range(n_templates)]
    for t in range(n_templates):
        for v in range(n_var):
            model.times(production[t], layout[t][v], printed[t][v]).post()

    # produced[v] is the number of copies of variation v printed from all templates together.
    # It is at least the demand for v.
    produced = [model.intvar(demand[v], n_slots * n_templates * ub, name=f"produced_{v}")
                for v in range(n_var)]
    for v in range(n_var):
        model.sum([printed[t][v] for t in range(n_templates)], "=", produced[v]).post()

    # total_sheets is the number of sheets printed in all.
    total_sheets = model.intvar(n_templates, n_templates * ub, name="total_sheets")
    model.sum(production, "=", total_sheets).post()

    # Each sheet carries one copy per slot, so the copies printed from a template are n_slots
    # times its sheets, and the copies of all variations together are n_slots times all sheets.
    for t in range(n_templates):
        model.scalar(printed[t] + [production[t]], [1] * n_var + [-n_slots], "=", 0).post()
    model.scalar(produced + [total_sheets], [1] * n_var + [-n_slots], "=", 0).post()

    # The objective is the number of sheets printed.
    return model, {"production": production, "layout": layout}, {"objective": total_sheets, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
