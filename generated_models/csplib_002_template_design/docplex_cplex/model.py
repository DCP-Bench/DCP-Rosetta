# csplib_002_template_design: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_002_template_design.py csplib_002_template_design.json

from docplex.mp.model import Model


def create_model(instance):
    """Template design: decide how many copies of each design variation to etch on each printing
    template (every template has a fixed number of slots, all filled) and how many sheets to print
    from each template, so that every variation's demand is met with as few sheets as possible."""
    n_slots = instance["n_slots"]          # slots on a template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand per variation
    ub = max(demand)                       # no template prints more sheets than the largest demand
    templates = range(n_templates)
    variations = range(n_var)

    model = Model("template_design")

    # production[i] is the number of sheets printed from template i, between 1 and the largest demand
    production = [model.integer_var(1, ub, name=f"production_{i}") for i in templates]

    # layout[i][v] is the number of copies of variation v on template i, at most n_slots (all the
    # slots of the template: a bound the statement does not give but the filled slots imply).
    # The demand rule multiplies layout by production, which CPLEX refuses for two variables.
    # Each layout is therefore written in binary, layout = sum 2^k * bit[k], and each product
    # bit[k] * production is a variable tied to it by the standard four inequalities.
    n_bits = n_slots.bit_length()  # enough bits to write 0..n_slots
    bit = {(i, v, k): model.binary_var(name=f"bit_{i}_{v}_{k}")
           for i in templates for v in variations for k in range(n_bits)}
    layout_vars = [[model.integer_var(0, n_slots, name=f"layout_{i}_{v}") for v in variations] for i in templates]
    for i in templates:
        for v in variations:
            model.add_constraint(layout_vars[i][v] == model.sum(2 ** k * bit[i, v, k] for k in range(n_bits)))

    # made[i, v, k] is bit[i, v, k] * production[i]: the sheets of template i when bit k of the
    # layout of variation v is set, else 0
    made = {}
    for i in templates:
        for v in variations:
            for k in range(n_bits):
                p = model.integer_var(0, ub, name=f"made_{i}_{v}_{k}")
                b = bit[i, v, k]
                model.add_constraint(p <= ub * b)
                model.add_constraint(p >= b)
                model.add_constraint(p <= production[i] - (1 - b))
                model.add_constraint(p >= production[i] - ub * (1 - b))
                made[i, v, k] = p

    # All slots of every template are populated.
    for i in templates:
        model.add_constraint(model.sum(layout_vars[i]) == n_slots)

    # The sheets printed meet the demand of every variation: the copies of a variation over all
    # templates, times the sheets printed from each, reach its demand.
    for v in variations:
        model.add_constraint(model.sum(2 ** k * made[i, v, k] for i in templates for k in range(n_bits))
                             >= demand[v])

    # Implied cut, added to tighten the relaxation: every template fills all its slots, so the
    # copies printed, n_slots per sheet, must reach the total demand.
    model.add_constraint(n_slots * model.sum(production) >= sum(demand))

    # Minimize the number of printed sheets.
    model.minimize(model.sum(production))

    return model, {"production": production, "layout": layout_vars}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
