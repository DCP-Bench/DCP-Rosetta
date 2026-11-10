# media_selection: a PySAT (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python media_selection.py media_selection.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Choose advertising media so that every target audience is reached by at least one
    chosen medium, at the lowest total campaign cost."""
    incidence_matrix = instance["incidence_matrix"]  # incidence_matrix[t][m]: 1 if medium m reaches audience t
    media_costs = instance["media_costs"]            # media_costs[m]: the cost of medium m
    n_audiences = len(instance["target_audiences"])  # the number of target audiences
    n_media = len(instance["advertising_media"])     # the number of advertising media

    pool = IDPool()

    # is_selected[m] is true when medium m is chosen for the campaign
    is_selected = [pool.id(("is_selected", m)) for m in range(n_media)]

    formula = WCNF()

    # Every audience is reached by at least one chosen medium. Reaching it more than once is fine.
    for t in range(n_audiences):
        # the media that reach audience t, and how strongly each one reaches it
        lits = [is_selected[m] for m in range(n_media) if incidence_matrix[t][m] != 0]
        weights = [incidence_matrix[t][m] for m in range(n_media) if incidence_matrix[t][m] != 0]
        if all(w == 1 for w in weights):
            # with no medium reaching audience t, this empty requirement can never hold
            formula.append(lits)
        else:
            formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=1, vpool=pool).clauses)

    # min_total_cost lies between the sum of the negative costs and the sum of the positive ones.
    # The range is never empty.
    low = sum(c for c in media_costs if c < 0)
    high = sum(c for c in media_costs if c > 0)
    min_total_cost = Integer("min_total_cost", low, max(high, low + 1), vpool=pool)
    formula.extend(IntegerEngine(vars=[min_total_cost], vpool=pool).clausify().clauses)

    # The campaign cost is built one medium at a time. partial[v] is true when the media
    # considered so far cost v in total. Before any medium is considered the total is 0.
    start = pool.id(("partial", 0, 0))
    formula.append([start])
    partial = {0: start}
    for m in range(n_media):
        nxt = {}
        for v in partial:
            for w in (v, v + media_costs[m]):
                if w not in nxt:
                    nxt[w] = pool.id(("partial", m + 1, w))
        for v, lit in partial.items():
            # medium m is left out and the total stays, or it is chosen and the total grows by its cost
            formula.append([-lit, is_selected[m], nxt[v]])
            formula.append([-lit, -is_selected[m], nxt[v + media_costs[m]]])
        partial = nxt

    # min_total_cost is the total cost of the chosen media.
    for v, lit in partial.items():
        formula.append([-lit, min_total_cost.equals(v)])
    # min_total_cost is only a total that some choice of media gives.
    for v in range(low, max(high, low + 1) + 1):
        if v not in partial:
            formula.append([-min_total_cost.equals(v)])

    # Spend as little as possible. A medium with a positive cost is paid for when it is chosen.
    # A medium with a negative cost is paid for when it is left out, which shifts every total by the same amount.
    for m in range(n_media):
        if media_costs[m] > 0:
            formula.append([-is_selected[m]], weight=media_costs[m])
        elif media_costs[m] < 0:
            formula.append([is_selected[m]], weight=-media_costs[m])

    # The objective in the problem's terms: the total cost of the chosen media (RC2's cost
    # differs from it by a fixed amount when some cost is negative).
    return formula, {"is_selected": is_selected, "min_total_cost": min_total_cost}, min_total_cost


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # an Integer decodes its value from the model, a literal is true when it is in the model
        value = np.vectorize(lambda v: v.decode(model) if isinstance(v, Integer) else v in model)
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
