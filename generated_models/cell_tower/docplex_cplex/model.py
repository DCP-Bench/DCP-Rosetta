# cell_tower: a CPLEX (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python cell_tower.py cell_tower.json

from docplex.mp.model import Model


def create_model(instance):
    """Cell towers: choose tower sites within the budget so that the covered population is as large as possible."""
    delta = instance["delta"]  # delta[i][j] is 1 if a tower at site i covers region j
    cost = instance["cost"]              # cost[i]: the cost of building a tower at site i
    population = instance["population"]  # population[j]: the number of inhabitants of region j
    budget = instance["budget"]          # the most the company can spend on towers
    sites = range(len(cost))
    regions = range(len(population))

    model = Model("cell_tower")

    # build_tower[i] is 1 when a tower is built at site i;
    # covered[j] is 1 when region j counts as covered.
    build_tower = model.binary_var_list(len(cost), name="build_tower")
    covered = model.binary_var_list(len(population), name="covered")

    # A region is covered only if at least one tower that covers it is built.
    model.add_constraints(covered[j] <= model.sum(delta[i][j] * build_tower[i] for i in sites)
                          for j in regions)

    # The towers built cost no more than the budget.
    model.add_constraint(model.dot(build_tower, cost) <= budget, ctname="budget")

    # Maximise the population of the covered regions.
    total_population_covered = model.dot(covered, population)
    model.maximize(total_population_covered)

    return model, {"build_tower": build_tower, "total_population_covered": total_population_covered}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
