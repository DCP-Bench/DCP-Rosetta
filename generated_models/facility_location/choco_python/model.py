# facility_location: a Choco-solver (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python facility_location.py facility_location.json

from pychoco.model import Model


def create_model(instance):
    """Choose which candidate warehouses to open, and how many units each open warehouse
    ships to each region, so that every region gets its weekly demand at the least total
    of fixed and shipping costs. Three rules restrict which warehouses may be open together."""
    names = instance["warehouse_s"]  # names[i]: the city of warehouse i
    fixed_costs = instance["fixed_costs"]  # fixed_costs[i]: the weekly fixed cost of warehouse i
    max_shipping = instance["max_shipping"]  # the most units one open warehouse ships per week
    demands = instance["demands"]  # demands[j]: the weekly demand of region j
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost per unit from warehouse i to region j
    n_warehouses = len(names)  # the number of candidate warehouses
    n_regions = len(demands)  # the number of regions

    # The rules name three cities, so look up their warehouse numbers.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    model = Model()

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [model.boolvar(name=f"open_{i}") for i in range(n_warehouses)]
    # ships[i][j] is the number of units sent from warehouse i to region j
    ships = [[model.intvar(0, max_shipping, name=f"ships_{i}_{j}") for j in range(n_regions)]
             for i in range(n_warehouses)]
    # total_cost is the cost of the plan, to minimise, kept below 10000
    total_cost = model.intvar(0, 10000, name="total_cost")

    # A warehouse ships at most max_shipping units, and nothing when it is closed.
    for i in range(n_warehouses):
        model.scalar(ships[i] + [open_warehouse[i]], [1] * n_regions + [-max_shipping], "<=", 0).post()

    # Every region receives at least its weekly demand.
    for j in range(n_regions):
        model.sum([ships[i][j] for i in range(n_warehouses)], ">=", demands[j]).post()

    # Rule 1: if the New York warehouse is open, the Los Angeles warehouse is open too.
    model.arithm(open_warehouse[new_york], "<=", open_warehouse[los_angeles]).post()

    # Rule 2: no more than three warehouses are open.
    model.sum(open_warehouse, "<=", 3).post()

    # Rule 3: the Atlanta warehouse or the Los Angeles warehouse (or both) is open.
    model.arithm(open_warehouse[atlanta], "+", open_warehouse[los_angeles], ">=", 1).post()

    # The cost of the plan is the fixed costs of the open warehouses plus the shipping cost of every route.
    flat_ships = [ships[i][j] for i in range(n_warehouses) for j in range(n_regions)]
    flat_costs = [shipping_costs[i][j] for i in range(n_warehouses) for j in range(n_regions)]
    model.scalar(flat_ships + open_warehouse, flat_costs + fixed_costs, "=", total_cost).post()

    return (
        model,
        {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships},
        {"objective": total_cost, "maximize": False},
    )


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
