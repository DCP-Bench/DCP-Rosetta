# cell_tower: a Z3 (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python cell_tower.py cell_tower.json

import z3


def create_model(instance):
    """A telecom company chooses at which potential sites to build cell towers, within a budget,
    to provide signal coverage to as many inhabitants of the city's regions as possible."""
    delta = instance["delta"]            # delta[i][j]: 1 when a tower at site i covers region j
    cost = instance["cost"]              # cost[i]: the cost of building a tower at site i
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    # the number of potential sites and the number of regions
    n_sites, n_regions = len(cost), len(population)

    # build_tower[i] is true when a tower is built at site i
    build_tower = [z3.Bool(f"build_tower_{i}") for i in range(n_sites)]
    # covered[j] is true when region j gets coverage
    covered = [z3.Bool(f"covered_{j}") for j in range(n_regions)]

    solver = z3.Optimize()

    # A region is covered only if some built tower reaches it.
    solver.add([
        z3.If(covered[j], 1, 0)
        <= z3.Sum([delta[i][j] * z3.If(build_tower[i], 1, 0) for i in range(n_sites)])
        for j in range(n_regions)
    ])
    # The cost of the towers built stays within the budget.
    solver.add(z3.Sum([z3.If(build_tower[i], cost[i], 0) for i in range(n_sites)]) <= budget)

    # Maximize the population covered.
    covered_population = z3.Sum([z3.If(covered[j], population[j], 0) for j in range(n_regions)])
    solver.maximize(covered_population)

    return solver, {"build_tower": build_tower, "total_population_covered": covered_population}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
