"""Template design: fill each template with variations and choose how many sheets to print from each,
meeting every variation's demand with as few printed sheets as possible."""
import hexaly.optimizer as hx


def build(instance):
    slots, templates = instance["n_slots"], instance["n_templates"]
    demand = instance["demand"]
    n_var = len(demand)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # layout[t][v] is the number of copies of variation v on template t
    layout = [[model.int(0, slots) for _ in range(n_var)] for _ in range(templates)]
    # production[t] is the number of sheets printed from template t. More than the largest demand
    # is never needed: that many sheets already meet the demand of every variation on the template.
    production = [model.int(0, max(demand)) for _ in range(templates)]

    # Each template has exactly n_slots slots
    for t in range(templates):
        model.constraint(model.sum(layout[t]) == slots)
    # The copies printed of each variation meet its demand
    for v in range(n_var):
        model.constraint(model.sum(layout[t][v] * production[t] for t in range(templates)) >= demand[v])

    # Minimise the total number of printed sheets
    model.minimize(model.sum(production))
    return optimizer, {"layout": layout, "production": production}
