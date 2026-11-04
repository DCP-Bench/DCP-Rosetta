# cell_tower: a PuLP (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python cell_tower.py cell_tower.json

import pulp


def create_model(instance):
    """A telecom company chooses which potential sites to build cell towers on,
    within its budget, to cover as many inhabitants of the city as possible."""
    delta = instance["delta"]            # delta[i][j]: 1 when a tower at site i reaches region j, 0 when not
    cost = instance["cost"]              # cost[i]: the cost of building a tower at site i
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    sites, regions = range(len(cost)), range(len(population))

    problem = pulp.LpProblem("cell_tower", pulp.LpMaximize)

    # build_tower[i] is 1 when a tower is built at site i, and 0 when not
    build_tower = [pulp.LpVariable(f"build_{i}", cat="Binary") for i in sites]
    # covered[j] is 1 when region j is reached by a built tower, and 0 when not
    covered = [pulp.LpVariable(f"covered_{j}", cat="Binary") for j in regions]

    # A region counts as covered only when a built tower reaches it.
    for j in regions:
        problem += covered[j] <= pulp.lpSum(delta[i][j] * build_tower[i] for i in sites)

    # The towers built cost no more than the budget.
    problem += pulp.lpSum(cost[i] * build_tower[i] for i in sites) <= budget

    # The inhabitants of the covered regions.
    reached = pulp.lpSum(population[j] * covered[j] for j in regions)

    # Maximize the population covered.
    problem += reached

    return problem, {"build_tower": build_tower, "total_population_covered": reached}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
