"""Media selection: select advertising media that reach every target audience at minimum cost."""
import hexaly.optimizer as hx


def build(instance):
    reaches = instance["incidence_matrix"]  # reaches[a][m] = 1 if medium m reaches audience a
    costs = instance["media_costs"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    is_selected = [model.bool() for _ in costs]

    # Every audience is reached by at least one selected medium
    for row in reaches:
        model.constraint(model.sum(is_selected[m] for m, r in enumerate(row) if r) >= 1)

    # Minimise the campaign cost
    min_total_cost = model.sum(c * s for c, s in zip(costs, is_selected))
    model.minimize(min_total_cost)
    return optimizer, {"is_selected": is_selected, "min_total_cost": min_total_cost}
