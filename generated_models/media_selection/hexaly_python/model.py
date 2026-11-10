"""Media selection: select advertising media that reach every target audience at minimum cost."""
import hexaly.optimizer as hx


def build(instance):
    reaches = instance["incidence_matrix"]  # reaches[a][m] = 1 if medium m reaches audience a (one row per target audience)
    costs = instance["media_costs"]  # costs[m] = cost of selecting medium m for the campaign
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is_selected[m] = 1 if medium m is selected for the campaign
    is_selected = [model.bool() for _ in costs]

    # All audiences are reached: each audience is covered by at least one selected medium
    # (being covered more than once is allowed)
    for row in reaches:
        model.constraint(model.sum(is_selected[m] for m, r in enumerate(row) if r) >= 1)

    # Minimise the campaign cost: the total cost of the selected media
    min_total_cost = model.sum(c * s for c, s in zip(costs, is_selected))
    model.minimize(min_total_cost)
    return optimizer, {"is_selected": is_selected, "min_total_cost": min_total_cost}
