from hermax.model import Model


def build(instance):
    demand = instance["demand"]          # copies needed of each variation
    n_slots = instance["n_slots"]        # variations that fit on one template
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]

    # Sheets per template never need to exceed the largest demand: if one
    # template printed more than that, one sheet fewer still meets every
    # demand, so such a template is not in an optimal solution.
    top = max(demand)
    bits = top.bit_length()

    m = Model()

    # layout[t][v]: copies of variation v etched on template t.
    layout = m.int_matrix("layout", n_templates, n_var, 0, n_slots)

    # production[t] is kept as binary digits, so every product with a copy
    # count is a Boolean-by-small-constant term, not an integer product.
    sheet_bits = [m.bool_vector(f"sheet_bit_{t}", bits) for t in range(n_templates)]
    production = [sum((2 ** b) * sheet_bits[t][b] for b in range(bits))
                  for t in range(n_templates)]
    for t in range(n_templates):
        m &= (production[t] <= top)

    # Each template holds at most n_slots variations.
    for t in range(n_templates):
        m &= (sum(layout[t][v] for v in range(n_var)) <= n_slots)

    # Copies printed of variation v: layout[t][v] * production[t], summed
    # over templates. Each term is the Boolean z = (layout == k) and
    # (bit b of production), weighted by k * 2^b.
    for v in range(n_var):
        terms = []
        for t in range(n_templates):
            for k in range(1, n_slots + 1):
                at_k = (layout[t][v] == k)
                for b in range(bits):
                    z = m.bool()
                    m &= (~z | at_k)
                    m &= (~z | sheet_bits[t][b])
                    terms.append((k * (2 ** b)) * z)
        # Every variation is printed at least as often as demanded.
        m &= (sum(terms) >= demand[v])

    # Minimise the total number of sheets printed.
    m.obj += sum(production)

    return m, {"layout": layout, "production": production}
