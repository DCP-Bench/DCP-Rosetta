# cell_tower: a PySAT (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python cell_tower.py cell_tower.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """A telecom company chooses at which potential sites to build cell towers, within a
    budget, to provide signal coverage to as many inhabitants of the city's regions as possible."""
    delta = instance["delta"]            # delta[i][j] is 1 when a tower at site i reaches region j
    cost = instance["cost"]              # cost[i]: the cost of a tower at site i
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    n_sites = len(cost)                  # the number of potential sites
    n_regions = len(population)          # the number of regions

    pool = IDPool()

    # build_tower[i] is true when a tower is built at site i
    build_tower = [pool.id(("build_tower", i)) for i in range(n_sites)]
    # covered_region[j] is true when region j is reached by a built tower
    covered_region = [pool.id(("covered_region", j)) for j in range(n_regions)]

    formula = WCNF()

    # A region is covered only if a tower built at a site that reaches it.
    for j in range(n_regions):
        formula.append([-covered_region[j]]
                       + [build_tower[i] for i in range(n_sites) if delta[i][j] > 0])

    # The towers built cost no more than the budget.
    formula.extend(PBEnc.leq(lits=build_tower, weights=cost, bound=budget, vpool=pool).clauses)

    # total_population_covered is the population of the covered regions. Its range runs from
    # the sum of the negative populations to the sum of the positive ones, and is at least one
    # wide, which is the most any choice of regions can reach.
    low = sum(p for p in population if p < 0)
    high = sum(p for p in population if p > 0)
    total = Integer("total_population_covered", low, max(high, low + 1), vpool=pool)
    # total takes exactly one value in its range.
    formula.extend(IntegerEngine(vars=[total], vpool=pool).clausify().clauses)

    # The total is the sum of the populations of the covered regions, added up one region at
    # a time. partial[v] is true when the regions added so far make v; only the sums that can
    # occur get a variable.
    start = pool.id(("partial", 0, 0))
    formula.append([start])
    partial = {0: start}
    for j in range(n_regions):
        # the sums that the first j + 1 regions can make
        nxt = {}
        for v in partial:
            for w in (v, v + population[j]):
                if w not in nxt:
                    nxt[w] = pool.id(("partial", j + 1, w))
        for v, lit in partial.items():
            # region j adds its population to the sum only when it is covered
            formula.append([-lit, covered_region[j], nxt[v]])
            formula.append([-lit, -covered_region[j], nxt[v + population[j]]])
        partial = nxt
    # The final sum is the total. A value that no choice of regions makes is ruled out.
    for v, lit in partial.items():
        formula.append([-lit, total.equals(v)])
    for v in range(low, max(high, low + 1) + 1):
        if v not in partial:
            formula.append([-total.equals(v)])

    # Maximise the population covered. Leaving a region with positive population uncovered
    # costs its population, and covering a region with negative population costs its size.
    for j in range(n_regions):
        if population[j] > 0:
            formula.append([covered_region[j]], weight=population[j])
        elif population[j] < 0:
            formula.append([-covered_region[j]], weight=-population[j])

    # The objective in the problem's terms: the population covered (RC2's cost is the
    # population left uncovered, plus the size of any negative region covered).
    return formula, {"build_tower": build_tower,
                     "total_population_covered": total}, total


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
