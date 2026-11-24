# diet: a CPLEX (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python diet.py diet.json

from docplex.mp.model import Model


def create_model(instance):
    """Diet: buy whole units of four foods so that every nutritional minimum is met at the least cost."""
    # Nutrients per unit of each food (cake, ice cream, cola, cheesecake), from the table in
    # the problem statement.
    CALORIES = [400, 200, 150, 500]
    CHOCOLATE = [3, 2, 0, 0]
    SUGAR = [2, 2, 4, 4]
    FAT = [2, 4, 1, 5]
    price = instance["price"]    # price[f]: the price of one unit of food f
    limits = instance["limits"]  # minimum calories, chocolate, sugar and fat
    foods = range(instance["n"])

    model = Model("diet")

    # x[f] is how many (whole) units of food f are bought
    x = model.integer_var_list(instance["n"], 0, name="x")

    # Each nutrient reaches its minimum.
    for name, per_unit, minimum in zip(("calories", "chocolate", "sugar", "fat"),
                                       (CALORIES, CHOCOLATE, SUGAR, FAT), limits):
        model.add_constraint(model.sum(per_unit[f] * x[f] for f in foods) >= minimum, ctname=name)

    # cost is the price of the diet. It is a variable of its own, not just the objective
    # expression, so that the declared output is this one integer rather than every quantity
    # behind it.
    cost = model.integer_var(0, name="cost")
    model.add_constraint(cost == model.sum(price[f] * x[f] for f in foods), ctname="price")

    # Minimise the cost.
    model.minimize(cost)

    return model, {"cost": cost}


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
