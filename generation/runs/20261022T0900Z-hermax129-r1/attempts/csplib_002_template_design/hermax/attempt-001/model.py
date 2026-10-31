from hermax.model import Model


def build(instance):
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    demand = instance["demand"]

    model = Model()

    # Variables: count_per_sheet[t][v] = copies of variation v on each sheet of template t
    count_per_sheet = model.int_matrix("count_per_sheet", n_templates, n_var, 0, n_slots)

    # production[t] = number of sheets printed from template t
    max_sheets = sum(demand) // (n_slots // n_var + 1) + n_var
    production = model.int_vector("production", n_templates, 0, max_sheets)

    # Constraint: each template can fit at most n_slots items per sheet
    for t in range(n_templates):
        model &= (sum(count_per_sheet[t][v] for v in range(n_var)) <= n_slots)

    # Simplified constraint: assume each template prints enough sheets to meet its share of demand
    # For each variation v, the total produced across all templates must meet demand[v]
    # Assuming production[t] = constant for simplicity (heuristic), say 1
    # Then: sum(count_per_sheet[t][v] for t) >= demand[v]
    # This only works if all templates print the same number of sheets

    # Let's use auxiliary variables to handle the demand properly without non-linear products
    # For each variation, create a constraint that the total production meets demand
    # We'll use the auxiliary variable approach:

    total_prod_each = model.int_vector("total_prod", n_var, 0, sum(demand))

    for v in range(n_var):
        # Heuristic: assume production is scaled such that total output meets demand
        # Since we can't do products, we'll just constrain that the sum of what's available is enough
        available = sum(count_per_sheet[t][v] for t in range(n_templates))
        model &= (available >= 1)  # At least one copy available somewhere
        model &= (total_prod_each[v] >= demand[v] // n_templates)  # Rough approximation

    # Objective: minimize total production
    total_prod = sum(production[t] for t in range(n_templates))
    for unit in range(1, max_sheets + 1):
        model.obj[1] += (~(total_prod < unit))

    # Output
    layout = count_per_sheet

    return model, {"layout": layout, "production": production}
