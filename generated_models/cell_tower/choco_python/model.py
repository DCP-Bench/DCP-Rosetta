# cell_tower: a Choco-solver (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python cell_tower.py cell_tower.json

from pychoco.model import Model


def create_model(instance):
    """A telecom company chooses at which potential sites to build cell towers, within its budget,
    so that as many inhabitants as possible live in a region that a built tower reaches."""
    delta = instance["delta"]            # delta[i][j]: 1 when a tower at site i reaches region j
    cost = instance["cost"]              # cost[i]: what a tower at site i costs
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    n_sites, n_regions = len(cost), len(population)

    model = Model()

    # build_tower[i] is true when a tower is built at site i
    build_tower = [model.boolvar(name=f"build_tower{i}") for i in range(n_sites)]
    # covered[j] is true when region j is reached by a built tower
    covered = [model.boolvar(name=f"covered{j}") for j in range(n_regions)]

    # A region is covered only if a built tower reaches it.
    for j in range(n_regions):
        # the sites whose tower would reach region j
        reach = [delta[i][j] for i in range(n_sites)]
        model.scalar(build_tower + [covered[j]], reach + [-1], ">=", 0).post()

    # The towers built cost no more than the budget.
    model.scalar(build_tower, cost, "<=", budget).post()

    # The number of inhabitants in the covered regions.
    total_population_covered = model.intvar(0, sum(population), name="total_population_covered")
    model.scalar(covered, population, "=", total_population_covered).post()

    # Maximize the population covered.
    return model, {
        "build_tower": build_tower,
        "total_population_covered": total_population_covered,
    }, {"objective": total_population_covered, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
