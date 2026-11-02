# cabling: a PySAT (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python cabling.py cabling.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Devices are placed one above another in a rack, one per slot, and some are joined by
    one or several cables. Order the devices so that the sum of all cable lengths is as short
    as possible."""
    n = instance["n"]                  # the number of devices, and of rack slots
    devices = instance["devices"]      # the names of the devices
    cables = instance["cable_struct"]  # for each pair of devices, the number of cables joining them

    # Cables name devices by name; pairs[c] gives the positions of the two devices joined by
    # cable group c, and the number of cables in it.
    pairs = [(devices.index(a), devices.index(b), count) for a, b, count in cables]
    slots = range(n)  # the rack slots, 0 to n - 1

    pool = IDPool()
    # x[d] is the rack slot of device d
    x = [Integer(f"x_{d}", 0, n - 1, vpool=pool) for d in range(n)]
    # dist[c] is the number of slots between the two devices of cable group c
    dist = [Integer(f"dist_{c}", 0, n - 1, encoding="order", vpool=pool) for c in range(len(pairs))]
    # final_sum is the total length of all cables. No cable spans more than n - 1 slots, so each
    # cable adds at most n - 1 to the total.
    n_cables = sum(count for _, _, count in pairs)
    final_sum = Integer("final_sum", 0, (n - 1) * n_cables, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=x + dist + [final_sum], vpool=pool)

    # Devices take different slots in the rack.
    engine.add_alldifferent(x)

    # The total length is the cables of each group times their distance, added up over all groups.
    engine.add_linear(sum(count * dist[c] for c, (_, _, count) in enumerate(pairs)) - final_sum == 0)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # The cables of a group span the slots between their two devices: if device a is in slot k
    # and device b in slot m, the distance is exactly the gap between k and m.
    for c, (a, b, _) in enumerate(pairs):
        for k in slots:
            for m in slots:
                if k == m:
                    continue
                gap = abs(k - m)
                # Each of these holds unless device a is in slot k and device b in slot m.
                elsewhere = [-x[a].equals(k), -x[b].equals(m)]
                formula.append(elsewhere + [dist[c].ge(gap)])
                # The distance cannot exceed n - 1, so the upper bound is only needed below that.
                if gap + 1 <= n - 1:
                    formula.append(elsewhere + [-dist[c].ge(gap + 1)])

    # Reversing the rack keeps every cable length, so device 0 is required to sit in a lower slot
    # than device 1.
    if n >= 2:
        for k in slots:
            for m in slots:
                if k >= m:
                    formula.append([-x[0].equals(k), -x[1].equals(m)])

    # A group of count cables pays count for every slot its distance reaches, so the total cost is
    # the sum of all cable lengths.
    for c, (_, _, count) in enumerate(pairs):
        if count > 0:
            for v in range(1, n):
                formula.append([-dist[c].ge(v)], weight=count)

    return formula, {"final_sum": final_sum}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
