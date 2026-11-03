# cell_tower: a Python-MIP (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python cell_tower.py cell_tower.json

import mip


def create_model(instance):
    """A telecom company chooses at which potential sites to build cell towers, within a budget,
    to provide signal coverage to as many inhabitants of the city's regions as possible."""
    delta = instance["delta"]            # delta[i][j]: 1 when a tower at site i reaches region j
    cost = instance["cost"]              # cost[i]: the cost of building a tower at site i
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    n_sites, n_regions = len(cost), len(population)

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # build_tower[i] is 1 when a tower is built at site i, and 0 when not
    build_tower = [model.add_var(f"build_tower_{i}", var_type=mip.BINARY) for i in range(n_sites)]
    # covered[j] is 1 when region j gets signal, and 0 when not
    covered = [model.add_var(f"covered_{j}", var_type=mip.BINARY) for j in range(n_regions)]
    # total_population_covered is the number of inhabitants of the covered regions
    total_population_covered = model.add_var(
        "total_population_covered", var_type=mip.INTEGER, lb=0, ub=sum(population))

    # A region gets signal only if a built tower reaches it.
    for j in range(n_regions):
        model += covered[j] <= mip.xsum(delta[i][j] * build_tower[i] for i in range(n_sites))

    # The cost of the towers built stays within the budget.
    model += mip.xsum(cost[i] * build_tower[i] for i in range(n_sites)) <= budget

    # The population covered is the total population of the covered regions.
    model += total_population_covered == mip.xsum(population[j] * covered[j] for j in range(n_regions))

    # Maximize the population covered.
    model.objective = total_population_covered

    return model, {"build_tower": build_tower, "total_population_covered": total_population_covered}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
