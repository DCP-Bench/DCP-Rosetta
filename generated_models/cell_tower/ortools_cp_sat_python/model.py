# cell_tower: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install ortools`):
#   python cell_tower.py cell_tower.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A telecom company chooses at which potential sites to build cell towers, within a budget,
    to provide signal coverage to as many inhabitants of the city's regions as possible."""
    # delta[i][j] is 1 when a tower at site i covers region j, otherwise 0
    delta = instance["delta"]
    cost = instance["cost"]              # cost[i]: the cost of building a tower at site i
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    # the number of potential sites and the number of regions
    n_sites, n_regions = len(cost), len(population)

    model = cp_model.CpModel()

    # build_tower[i] is true when a tower is built at site i
    build_tower = [model.new_bool_var(f"b_{i}") for i in range(n_sites)]
    # covered[j] is true when region j gets coverage
    covered = [model.new_bool_var(f"c_{j}") for j in range(n_regions)]

    # A region is covered only if some built tower reaches it.
    for j in range(n_regions):
        model.add(covered[j] <= sum(delta[i][j] * build_tower[i] for i in range(n_sites)))
    # The cost of the built towers stays within the budget.
    model.add(sum(c * b for c, b in zip(cost, build_tower)) <= budget)

    # The population covered is the population of the covered regions.
    total_population_covered = sum(p * c for p, c in zip(population, covered))

    # Maximize the population covered.
    model.maximize(total_population_covered)

    return model, {
        "build_tower": build_tower,
        "total_population_covered": total_population_covered,
    }


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
