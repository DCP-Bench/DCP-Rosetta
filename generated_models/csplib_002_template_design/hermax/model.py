# csplib_002_template_design: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_002_template_design.py csplib_002_template_design.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Template design: a colour printing firm prints several variations of a carton design
    from templates, each with n_slots slots, one copy per slot. Decide how many templates
    to use, which variations and how many copies of each go on each template, and how many
    sheets are printed from each template, so that every variation is printed at least as
    often as its demand, using as few printed sheets in all as possible."""
    demand = instance["demand"]              # demand[v]: copies of variation v that must be printed
    n_slots = instance["n_slots"]            # n_slots: slots on one template, each filled by one copy
    n_templates = instance["n_templates"]    # n_templates: how many templates may be produced
    n_var = instance["n_var"]                # n_var: number of design variations

    total_demand = sum(demand)               # all copies that must be printed, over all variations
    # Implied bound on the sheets printed from one template (safe for optimality: it cannot cut
    # off an optimum). When every variation fits on one template (n_var <= n_slots), a single
    # template with a copy of each variation and max(demand) sheets already meets every demand,
    # so an optimum prints at most max(demand) sheets in all, and so at most that many from any
    # one template. Otherwise, put each variation on some template and print from each template
    # the largest demand among its variations: that prints at most total_demand sheets in all,
    # so an optimum prints at most total_demand from any one template.
    sheet_bound = max(demand) if n_var <= n_slots else total_demand

    m = Model()

    # layout[t][v] is the number of copies of variation v on template t (the declared layout)
    layout = [m.int_vector(f"layout_{t}", n_var, 0, n_slots) for t in range(n_templates)]

    # Sheets printed from each template, written in binary: production[t] is the sum of
    # 2**b * bit[t][b] over the bits b of the sheet count, so production[t] is 0 when no bit is on.
    # Limitation: hermax cannot multiply two wide integers (a sheet count up to sheet_bound by a
    # layout count up to n_slots), and a case split over the sheet count is too slow to solve
    # the larger instances. The binary digits keep every product to a small integer times a
    # Boolean.
    n_bits = sheet_bound.bit_length()  # binary digits needed to write sheet_bound
    bit = [m.bool_vector(f"bit_{t}", n_bits) for t in range(n_templates)]  # bit[t][b]: digit b of production[t]
    production = [sum_expr(2 ** b * bit[t][b] for b in range(n_bits)) for t in range(n_templates)]
    # The sheets from one template cannot exceed the bound.
    for t in range(n_templates):
        m &= (production[t] <= sheet_bound)
    # Templates are interchangeable: order them by the number of sheets printed from each.
    for t in range(n_templates - 1):
        m &= (production[t] >= production[t + 1])

    # Every template fills all its slots with copies.
    for t in range(n_templates):
        m &= (sum(layout[t][v] for v in range(n_var)) == n_slots)

    # part[t][v][b] is layout[t][v] when bit b of production[t] is on, and 0 otherwise, so
    # that sum over b of 2**b * part[t][v][b] is production[t] * layout[t][v].
    part = [[[m.int(f"part_{t}_{v}_{b}", 0, n_slots) for b in range(n_bits)]
             for v in range(n_var)] for t in range(n_templates)]
    for t in range(n_templates):
        for v in range(n_var):
            for b in range(n_bits):
                m &= (part[t][v][b] == layout[t][v]).only_if(bit[t][b])
                m &= (part[t][v][b] == 0).only_if(~bit[t][b])

    # printed[v] is the number of copies of variation v printed over all templates:
    # the sum over t of production[t] * layout[t][v].
    printed = [sum_expr(2 ** b * part[t][v][b] for t in range(n_templates) for b in range(n_bits))
               for v in range(n_var)]
    # Every variation is printed at least as often as its demand.
    for v in range(n_var):
        m &= (printed[v] >= demand[v])

    # Total sheets printed, over all templates.
    total_sheets = sum_expr(production)

    # Implied: every sheet carries n_slots copies, so the copies printed in all, n_slots times the
    # sheets, must cover the total demand.
    m &= (n_slots * total_sheets >= total_demand)
    # Implied: the copies of variation v printed, plus the demand of all other variations, cannot
    # exceed the copies printed in all (n_slots times the sheets).
    for v in range(n_var):
        m &= (printed[v] + (total_demand - demand[v]) <= n_slots * total_sheets)

    # Minimise the total number of sheets printed.
    m.obj += total_sheets

    # The objective in the problem's terms: the total number of sheets printed, the cost minimised above.
    return m, {"production": production, "layout": layout}, total_sheets


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
