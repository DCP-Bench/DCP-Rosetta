# cell_tower: an Exact (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python cell_tower.py cell_tower.json

from exact import Exact


def create_model(instance):
    """A telecom company chooses which potential sites to build cell towers on, within a budget,
    to cover as many inhabitants of the city's regions as possible."""
    delta = instance["delta"]            # delta[i][j]: 1 when a tower at site i covers region j, otherwise 0
    cost = instance["cost"]              # cost[i]: the cost of building a tower at site i
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    n_sites, n_regions = len(cost), len(population)

    solver = Exact()

    # Exact identifies its variables by name.
    # build_tower[i] is 1 when a tower is built at site i, and 0 when not
    build_tower = [f"build_tower{i}" for i in range(n_sites)]
    # covered[j] is 1 when region j gets coverage, and 0 when not
    covered = [f"covered{j}" for j in range(n_regions)]
    for name in build_tower + covered:
        solver.addVariable(name, 0, 1)

    # A region is covered only if a built tower reaches it.
    for j in range(n_regions):
        reach = [(delta[i][j], build_tower[i]) for i in range(n_sites)]  # the towers that reach region j
        solver.addConstraint(reach + [(-1, covered[j])], True, 0)

    # The towers built cost no more than the budget.
    solver.addConstraint(list(zip(cost, build_tower)), False, 0, True, budget)

    # The population covered is the total population of the covered regions.
    solver.addVariable("total_population_covered", 0, sum(population))
    solver.addConstraint(list(zip(population, covered)) + [(-1, "total_population_covered")], True, 0, True, 0)

    # Cover as many inhabitants as possible.
    solver.setObjective([(1, "total_population_covered")], minimize=False)

    return solver, {"build_tower": build_tower, "total_population_covered": "total_population_covered"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
