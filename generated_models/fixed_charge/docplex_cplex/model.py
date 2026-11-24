# fixed_charge: a CPLEX (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python fixed_charge.py fixed_charge.json

from docplex.mp.model import Model


def create_model(instance):
    """Fixed charge: decide which machines to rent and how much of each product to make, for maximum profit."""
    machines = instance["machines"]    # machine indices
    products = instance["products"]    # product indices
    resources = instance["resources"]  # resource indices (labour, cloth)
    renting_cost = instance["renting_cost"]  # renting_cost[m]: the cost of renting machine m, paid once
    capacity = instance["capacity"]          # capacity[r]: the amount of resource r available
    product = instance["product"]      # product[p] = [profit per unit, machine it needs]
    use = instance["use"]              # use[p][r]: amount of resource r one unit of p needs
    max_production = instance["max_production"]  # the most units that can be made of any product

    model = Model("fixed_charge")

    # rent[m] is 1 when machine m is rented; produce[p] is how much of product p is made.
    rent = {m: model.binary_var(name=f"rent_{m}") for m in machines}
    produce = {p: model.integer_var(0, max_production, name=f"produce_{p}") for p in products}

    # Production uses no more labour or cloth than is available.
    model.add_constraints((model.sum(use[p][r] * produce[p] for p in products) <= capacity[r]
                           for r in resources), names=[f"capacity_{r}" for r in resources])

    # A product can be made only if the machine it needs is rented.
    # (max_production is the most that can be made, so it is as large as the units can get)
    model.add_constraints((produce[p] <= max_production * rent[product[p][1]] for p in products),
                          names=[f"machine_{p}" for p in products])

    # z is the profit: the profit on the units made, less the rent of the machines. It is a
    # variable of its own so that the reported output is one variable; it is never negative,
    # since making nothing rents nothing and earns 0.
    z = model.integer_var(name="z")
    model.add_constraint(z == model.sum(product[p][0] * produce[p] for p in products)
                         - model.sum(renting_cost[m] * rent[m] for m in machines), ctname="profit")

    # Maximise the profit.
    model.maximize(z)

    return model, {"z": z}


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
