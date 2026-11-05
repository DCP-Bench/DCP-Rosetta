# tsp: a PySAT (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python tsp.py tsp.json

import math

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def full_adder(formula, pool, x, y, carry_in):
    """Add three bits. Returns the sum bit and the carry bit."""
    s, carry = pool.id(), pool.id()
    for vx in (True, False):
        for vy in (True, False):
            for vc in (True, False):
                odd = vx ^ vy ^ vc
                formula.append([-x if vx else x, -y if vy else y,
                                -carry_in if vc else carry_in, s if odd else -s])
    formula.extend([[-x, -y, carry], [-x, -carry_in, carry], [-y, -carry_in, carry],
                    [x, y, -carry], [x, carry_in, -carry], [y, carry_in, -carry]])
    return s, carry


def add_numbers(formula, pool, xs, ys, false):
    """Add two binary numbers, given as bit lists from the lowest bit up."""
    length = max(len(xs), len(ys))
    xs = xs + [false] * (length - len(xs))
    ys = ys + [false] * (length - len(ys))
    out, carry = [], false
    for x, y in zip(xs, ys):
        s, carry = full_adder(formula, pool, x, y, carry)
        out.append(s)
    return out + [carry]


def arc_duals(dist):
    """Amounts row[i] and col[j] that can be subtracted from the arcs leaving city i and
    entering city j without changing which route is shortest. Found with the Hungarian
    method on the distance table, where an arc from a city to itself costs more than any
    other arc."""
    n = len(dist)
    big = sum(max(r) for r in dist) + 1  # the cost of an arc from a city to itself
    row = [0] * (n + 1)  # index 0 is a placeholder; row[i + 1] belongs to city i
    col = [0] * (n + 1)  # index 0 is a placeholder; col[j + 1] belongs to city j
    match = [0] * (n + 1)  # match[j] is the row assigned to column j
    for i in range(1, n + 1):
        match[0] = i
        j0 = 0
        least = [float("inf")] * (n + 1)
        via = [0] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = match[j0], float("inf"), 0
            for j in range(1, n + 1):
                if not used[j]:
                    c = (big if i0 == j else dist[i0 - 1][j - 1]) - row[i0] - col[j]
                    if c < least[j]:
                        least[j], via[j] = c, j0
                    if least[j] < delta:
                        delta, j1 = least[j], j
            for j in range(n + 1):
                if used[j]:
                    row[match[j]] += delta
                    col[j] -= delta
                else:
                    least[j] -= delta
            j0 = j1
            if match[j0] == 0:
                break
        while j0:
            j1 = via[j0]
            match[j0] = match[j1]
            j0 = j1
    return row[1:], col[1:]


def create_model(instance):
    """Find the shortest route that visits every city exactly once and returns to the
    starting city. The distance between two cities is their Euclidean distance rounded
    to an integer, and the output is the length of that route."""
    locations = instance["locations"]  # locations[i]: the (x, y) coordinates of city i
    n = len(locations)                 # the number of cities

    # dist[i][j]: the distance between city i and city j, rounded to an integer
    dist = [[int(round(math.hypot(a[0] - b[0], a[1] - b[1]))) if i != j else 0
             for j, b in enumerate(locations)] for i, a in enumerate(locations)]

    pool = IDPool()
    formula = WCNF()

    # A variable that is true. Its negation stands for a bit that is always 0.
    true = pool.id("true")
    formula.append([true])
    false = -true

    # succ[i][j] is true when the route goes from city i directly to city j
    succ = [[pool.id(("succ", i, j)) if i != j else None for j in range(n)]
            for i in range(n)]

    # Each city is left by exactly one arc and entered by exactly one arc.
    for i in range(n):
        out = [succ[i][j] for j in range(n) if j != i]
        into = [succ[j][i] for j in range(n) if j != i]
        for lits in (out, into):
            formula.extend(CardEnc.equals(lits=lits, bound=1, vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    # The route is a single circuit with no sub-loops. With more than two cities, each city
    # other than the start gets a place from 1 to n-1 along the route, and when the route goes
    # from i to j (neither the start), j has a later place than i. A loop that avoids the start
    # would need places that increase all the way round, which is impossible.
    pos = {}
    if n > 2:
        for i in range(1, n):
            pos[i] = Integer(f"position_{i}", 1, n - 1, encoding="order", vpool=pool)
            formula.extend(pos[i].domain_clauses())
        for i in range(1, n):
            for j in range(1, n):
                if i == j:
                    continue
                for t in range(1, n):
                    # If the route goes from i to j and i is at place t or later, then j is at place t + 1 or later.
                    clause = [-succ[i][j]]
                    if t > 1:
                        clause.append(-pos[i].ge(t))
                    if t + 1 <= n - 1:
                        clause.append(pos[j].ge(t + 1))
                    formula.append(clause)

    # Length of the nearest-neighbour tour: from the start, go to the nearest city not yet
    # visited, and finally return to the start.
    tour_length = 0
    here, seen = 0, {0}
    while len(seen) < n:
        nearest = min((j for j in range(n) if j not in seen), key=lambda j: dist[here][j])
        tour_length += dist[here][nearest]
        seen.add(nearest)
        here = nearest
    tour_length += dist[here][0]

    # Bits needed to write the tour length in binary.
    n_bits = max(tour_length.bit_length(), 1)

    # The route length in binary, lowest bit first: the sum of the distances of the arcs taken.
    total = [false]
    for i in range(n):
        # arc_bits[k] is true when the arc taken from city i has bit k set in its distance.
        longest = max([dist[i][j] for j in range(n) if j != i] + [0])
        n_arc_bits = max(longest.bit_length(), 1)
        arc_bits = []
        for k in range(n_arc_bits):
            taken = [succ[i][j] for j in range(n) if j != i and (dist[i][j] >> k) & 1]
            if not taken:
                arc_bits.append(false)
                continue
            bit = pool.id(("arc_bit", i, k))
            formula.append([-bit] + taken)
            for lit in taken:
                formula.append([-lit, bit])
            arc_bits.append(bit)
        total = add_numbers(formula, pool, total, arc_bits, false)

    # The route is no longer than the nearest-neighbour tour. Bits above the top bit of the tour
    # length are 0, and no length has a 1 where the tour length has a 0 while all higher bits agree.
    for k in range(n_bits, len(total)):
        formula.append([-total[k]])
    bits = total[:n_bits]
    for k in range(n_bits):
        if not (tour_length >> k) & 1:
            clause = [-bits[k]]
            for j in range(k + 1, n_bits):
                clause.append(-bits[j] if (tour_length >> j) & 1 else bits[j])
            formula.append(clause)

    # travel_distance is the route length. Its value is the number that the bits spell.
    travel_distance = Integer("travel_distance", 0, max(tour_length, 1), vpool=pool)
    for v in range(0, max(tour_length, 1) + 1):
        lit = travel_distance.equals(v)
        if v > tour_length:
            formula.append([-lit])
            continue
        spelled = [bits[k] if (v >> k) & 1 else -bits[k] for k in range(n_bits)]
        for s in spelled:
            formula.append([-lit, s])
        formula.append([lit] + [-s for s in spelled])

    # With more than two cities, the route never goes from i to j and straight back from j to i.
    if n > 2:
        for i in range(n):
            for j in range(i + 1, n):
                formula.append([-succ[i][j], -succ[j][i]])

    # Minimise the route length. The soft constraints pay the reduced distance of each arc.
    # Subtracting row[i] from the arcs leaving city i and col[j] from the arcs entering city j
    # shifts every route by the same total, since each city is left and entered once. The
    # amounts keep every reduced distance non-negative.
    row, col = arc_duals(dist)
    for i in range(n):
        for j in range(n):
            if i != j:
                reduced = dist[i][j] - row[i] - col[j]
                if reduced > 0:
                    formula.append([-succ[i][j]], weight=reduced)

    # The objective in the problem's terms: the route length, the distance of each arc driven
    # (RC2's cost pays reduced distances, a fixed amount less).
    objective = [(dist[i][j], succ[i][j]) for i in range(n) for j in range(n) if i != j]

    return formula, {"travel_distance": travel_distance}, objective


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
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
