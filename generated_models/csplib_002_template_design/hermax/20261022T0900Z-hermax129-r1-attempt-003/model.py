from hermax.model import Model


def build(instance):
    demand = instance["demand"]
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]

    # A template never needs more sheets than the largest demand: with more sheets,
    # every variation it carries is already covered by that template alone, so the
    # count can be lowered to the largest demand without losing coverage.
    max_sheets = max(demand)

    m = Model()
    layout = m.int_matrix("layout", n_templates, n_var, 0, n_slots)
    production = m.int_vector("production", n_templates, 0, max_sheets)

    # Each template has n_slots positions, and each position carries one copy of one variation.
    for t in range(n_templates):
        m &= (sum(layout[t][v] for v in range(n_var)) <= n_slots)

    # Copies of variation v printed from template t: sheets times copies on the template.
    # The copy count is the smaller factor (0 to n_slots), so the product is written as a
    # case split over that factor.
    copies = [[m.int(f"copies_{t}_{v}", 0, demand[v]) for v in range(n_var)]
              for t in range(n_templates)]
    for t in range(n_templates):
        for v in range(n_var):
            m &= (copies[t][v] == 0).only_if(layout[t][v] == 0)
            for k in range(1, n_slots + 1):
                m &= (copies[t][v] <= k * production[t]).only_if(layout[t][v] == k)

    # Every variation must be printed at least as many times as its demand, summed over all templates.
    for v in range(n_var):
        m &= (sum(copies[t][v] for t in range(n_templates)) >= demand[v])

    # Every slot prints one copy, so the sheets must cover the total demand over n_slots.
    total_demand = sum(demand)
    m &= (sum(production[t] for t in range(n_templates)) * n_slots >= total_demand)

    # Templates are interchangeable, so list them by sheet count (largest first).
    for t in range(n_templates - 1):
        m &= (production[t] >= production[t + 1])

    # Minimise the total number of printed sheets.
    m.obj += sum(production[t] for t in range(n_templates))

    return m, {"layout": layout, "production": production}
