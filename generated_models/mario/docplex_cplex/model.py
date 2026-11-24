# mario: a CPLEX (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python mario.py mario.json

from docplex.mp.model import Model


def create_model(instance):
    """Mario: plan a route from Mario's house to Luigi's house through other houses, collecting as much
    gold as possible, without the fuel spent on the way exceeding the fuel limit."""
    n = instance["nHouses"]             # the number of houses
    mario = instance["marioHouse"]      # the house where Mario starts
    luigi = instance["luigiHouse"]      # the house where Mario ends
    fuel_limit = instance["fuelLimit"]  # the most fuel Mario can spend
    arc_fuel = instance["arc_fuel"]   # arc_fuel[i][j]: fuel to go from house i to house j
    gold = instance["goldInHouse"]    # gold collected by visiting a house
    houses = range(n)

    model = Model("mario")

    # go[i, j] = 1 when house j is the successor of house i; go[i, i] = 1 means house i is not
    # on the route. Successor binaries keep the output a linear expression over binaries.
    go = model.binary_var_matrix(houses, houses, name="go")

    # Every house has exactly one successor, and every house is the successor of exactly one
    # house (the successors are all different).
    model.add_constraints(model.sum(go[i, j] for j in houses) == 1 for i in houses)
    model.add_constraints(model.sum(go[j, i] for j in houses) == 1 for i in houses)

    # The route ends at Luigi's house, which loops back to Mario's house.
    model.add_constraint(go[luigi, mario] == 1)

    # order[i] is the rank of house i on the route; Mario's house is first. Along every arc of
    # the route other than the one back into Mario's house the rank goes up by one, so the
    # houses on the route form a single path from Mario to Luigi and no detached loop can exist.
    order = model.integer_var_list(n, 1, n, name="order")
    model.add_constraint(order[mario] == 1)
    for i in houses:
        for j in houses:
            if i != j and j != mario:
                model.add_indicator(go[i, j], order[j] == order[i] + 1)

    # The fuel consumed along the chosen arcs may not exceed the fuel limit.
    model.add_constraint(model.sum(arc_fuel[i][j] * go[i, j] for i in houses for j in houses) <= fuel_limit)

    # Maximize the gold of the houses on the route (those that are not their own successor).
    model.maximize(model.sum(gold[i] * (1 - go[i, i]) for i in houses))

    # s[i] is the house that follows house i (i itself when it is not on the route).
    s = [model.sum(j * go[i, j] for j in houses) for i in houses]
    return model, {"s": s}


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
