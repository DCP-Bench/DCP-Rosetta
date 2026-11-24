# bananas: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python bananas.py

from docplex.mp.model import Model


def create_model(instance):
    """Bananas: five bananas cost $3, seven oranges $5, nine mangoes $7 and three apples $9. Buy 100
    fruits for $100, at least one of every kind, with as few bananas and apples together as possible."""
    total_fruits = 100   # fruits to buy (puzzle constant)
    total_dollars = 100  # money to spend (puzzle constant)
    # (fruits in a pack, dollars the pack costs): bananas, oranges, mangoes, apples (puzzle constant)
    packs = [(5, 3), (7, 5), (9, 7), (3, 9)]
    scale = 5 * 7 * 9 * 3  # a common multiple of the pack sizes: makes every price per fruit an integer

    model = Model("bananas")

    # How many of each fruit is bought: at least one of every kind, and at most all the fruits.
    bananas = model.integer_var(1, total_fruits, name="bananas")
    oranges = model.integer_var(1, total_fruits, name="oranges")
    mangoes = model.integer_var(1, total_fruits, name="mangoes")
    apples = model.integer_var(1, total_fruits, name="apples")

    # The fruits cost 100 dollars: 3/5 of a dollar per banana, 5/7 per orange, 7/9 per mango and
    # 9/3 per apple; both sides are multiplied by scale to keep the coefficients integers.
    quantities = [bananas, oranges, mangoes, apples]
    model.add_constraint(model.sum(dollars * (scale // fruits) * quantity
                                   for (fruits, dollars), quantity in zip(packs, quantities))
                         == total_dollars * scale)

    # 100 fruits are bought.
    model.add_constraint(bananas + oranges + mangoes + apples == total_fruits)

    # Minimize the number of bananas and apples together.
    model.minimize(bananas + apples)

    return model, {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}


if __name__ == "__main__":
    model, outputs = create_model({})
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
