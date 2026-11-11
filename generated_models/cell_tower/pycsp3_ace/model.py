# cell_tower: a PyCSP3 model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python cell_tower.py cell_tower.json

from pycsp3 import *


def create_model(instance):
    """A telecom company chooses which potential cell tower sites to build. Each tower
    has a cost and covers some regions of the city; each region has a population.
    With a limited budget, build towers to cover as many people as possible."""
    budget = instance["budget"]          # the money available for building towers
    cost = instance["cost"]              # cost[s]: the cost of building a tower at site s
    delta = instance["delta"]            # delta[s][r] = 1 if a tower at site s reaches region r
    population = instance["population"]  # population[r]: the number of inhabitants of region r
    n_sites = len(cost)
    n_regions = len(population)

    # build_tower[s] is 1 when a tower is built at site s
    build_tower = VarArray(size=n_sites, dom={0, 1})

    # covered[r] is 1 when region r is covered by a built tower
    covered = VarArray(size=n_regions, dom={0, 1})

    # total: the number of inhabitants covered; cannot exceed the whole city population
    total = Var(dom=range(sum(population) + 1))

    satisfy(
        # The towers built fit within the budget.
        Sum(cost[s] * build_tower[s] for s in range(n_sites)) <= budget,
        # The covered population is the sum of the populations of the covered regions.
        total == Sum(population[r] * covered[r] for r in range(n_regions)),
    )

    # A region is covered only when a built tower reaches it. Maximising the covered
    # population makes each covered flag as large as the built towers allow.
    for r in range(n_regions):
        sites_reaching_r = [s for s in range(n_sites) if delta[s][r] == 1]
        if sites_reaching_r:
            satisfy(covered[r] <= Sum(build_tower[s] for s in sites_reaching_r))
        else:
            # No site reaches region r, so it stays uncovered.
            satisfy(covered[r] == 0)

    # Maximise the total covered population.
    maximize(total)

    return {"build_tower": build_tower, "total_population_covered": total}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("build_tower =", values(outputs["build_tower"]))
        print("total_population_covered =", value(outputs["total_population_covered"]))
    else:
        print("No solution:", status())
