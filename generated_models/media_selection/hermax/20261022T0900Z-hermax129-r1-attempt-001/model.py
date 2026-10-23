from hermax.model import Model


def build(instance):
    costs = instance["media_costs"]
    incidence = instance["incidence_matrix"]
    n_media = len(costs)
    n_audiences = len(incidence)

    m = Model()
    # select[j] is true when media j is bought.
    select = m.bool_vector("select", n_media)

    # Every audience must be reached by at least one selected medium.
    for i in range(n_audiences):
        covering = [select[j] for j in range(n_media) if incidence[i][j]]
        m &= (sum(covering) >= 1)

    # Minimise the total campaign cost of the selected media.
    total_cost = sum(costs[j] * select[j] for j in range(n_media))
    m.obj += total_cost

    return m, {"is_selected": select, "min_total_cost": total_cost}
