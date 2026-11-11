# session1_money_change: a CPLEX (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session1_money_change.py session1_money_change.json

from docplex.mp.model import Model


def create_model(instance):
    """Alice gives Bob change: she composes the amount from the coins she has of each type,
    using as few coins as possible."""
    amount = instance["amount"]              # the change Alice has to give Bob
    values = instance["types_of_coins"]      # values[i]: the value of a coin of type i
    available = instance["available_coins"]  # available[i]: how many coins of type i Alice has
    n_types = len(values)

    model = Model("money_change")

    # coin_counts[i] is how many coins of type i Alice gives, at most the number
    # she has of that type.
    coin_counts = [model.integer_var(0, available[i], name=f"coin_counts_{i}") for i in range(n_types)]

    # The coins given add up to the amount owed.
    model.add_constraint(model.dot(coin_counts, values) == amount, ctname="amount")

    # Minimise the number of coins given.
    model.minimize(model.sum(coin_counts))

    return model, {"coin_counts": coin_counts}


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
