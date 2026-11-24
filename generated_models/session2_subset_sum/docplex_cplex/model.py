# session2_subset_sum: a CPLEX (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session2_subset_sum.py session2_subset_sum.json

from docplex.mp.model import Model


def create_model(instance):
    """Thieves stole some bags of coins from a bank van, a total of a given number of coins. Find how
    many bags were stolen of each type of coin bag."""
    total = instance["total_coins_lost"]  # the number of coins lost in all
    coins = instance["coin_numbers"]      # coins[i]: the number of coins in a bag of type i

    model = Model("subset_sum")

    # bags[i] is the number of bags of type i stolen. At most total of them: a bag holds at least
    # one coin, so more bags than coins lost cannot be stolen. This cuts off no solution.
    bags = model.integer_var_list(len(coins), 0, total, name="bags")

    # The coins in the stolen bags add up to the coins lost.
    model.add_constraint(model.dot(bags, coins) == total, ctname="total")

    return model, {"bags": bags}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
