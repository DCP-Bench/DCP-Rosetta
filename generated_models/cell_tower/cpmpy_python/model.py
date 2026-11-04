# cell_tower: a CPMpy model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python cell_tower.py cell_tower.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """A telecom company chooses at which potential sites to build cell towers, within a budget, to
    provide signal coverage to as many inhabitants of the city's regions as possible."""
    delta = np.array(instance["delta"])  # delta[i][j]: 1 when a tower at site i covers region j
    cost = instance["cost"]              # cost[i]: the cost of building a tower at site i
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    sites, regions = delta.shape

    # build_tower[i] is true when a tower is built at site i
    build_tower = cp.boolvar(shape=sites, name="build_tower")
    # covered[j] is true when region j gets coverage
    covered = cp.boolvar(shape=regions, name="covered")
    # total_population_covered is the number of inhabitants of the covered regions
    total_population_covered = cp.intvar(0, sum(population), name="total_population_covered")

    model = cp.Model()
    # A region is covered only if some built tower reaches it.
    model.add(covered <= build_tower @ delta)
    # The cost of the built towers stays within the budget.
    model.add(cp.sum(build_tower * cost) <= budget)
    # The population covered is the population of the covered regions.
    model.add(total_population_covered == cp.sum(covered * population))

    # Maximise the population covered.
    model.maximize(total_population_covered)

    return model, {"build_tower": build_tower, "total_population_covered": total_population_covered}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
