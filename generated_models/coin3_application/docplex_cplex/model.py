# coin3_application: a CPLEX (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python coin3_application.py coin3_application.json

from docplex.mp.model import Model


def create_model(instance):
    """Coin set: the fewest coins from which every amount below the maximum can be paid exactly."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of kind i
    max_amount = instance["max_amount_to_pay"]  # every amount smaller than this must be payable
    kinds = range(len(denominations))
    amounts = range(1, max_amount)              # the amounts to pay: 1 .. max_amount - 1

    model = Model("coin3_application")

    # x[i] is how many coins of kind i are in the set.
    x = model.integer_var_list(len(kinds), name="x")

    # Every amount is paid exactly by some selection of the coins in the set: pay[j, i] is how
    # many coins of kind i pay amount j, never more than the set holds.
    pay = model.integer_var_matrix(amounts, kinds, name="pay")
    model.add_constraints(model.sum(denominations[i] * pay[j, i] for i in kinds) == j for j in amounts)
    model.add_constraints(pay[j, i] <= x[i] for j in amounts for i in kinds)

    # Minimise the number of coins in the set.
    model.minimize(model.sum(x))

    return model, {"x": x}


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
