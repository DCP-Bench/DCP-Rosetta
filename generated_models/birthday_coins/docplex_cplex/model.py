# birthday_coins: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python birthday_coins.py

from docplex.mp.model import Model


def create_model(instance):
    """Birthday coins: Tommy got 15 coins, half-crowns, shillings and sixpences, worth 1 pound 5
    shillings 6 pence in all. How many half-crowns did he get?"""
    half_crown, shilling, sixpence = 30, 12, 6  # value of each kind of coin, in pence
    total_value = (20 + 5) * 12 + 6   # 1 pound 5 shillings 6 pence in pence: 25 shillings of 12 pence, and 6 more
    total_coins = 15                  # the number of coins Tommy was given

    model = Model("birthday_coins")

    # How many coins of each kind Tommy was given (none of a kind is allowed, no more than all of them).
    half_crowns = model.integer_var(0, total_coins, name="half_crowns")
    shillings = model.integer_var(0, total_coins, name="shillings")
    sixpences = model.integer_var(0, total_coins, name="sixpences")

    # The coins add up to 1 pound 5 shillings 6 pence.
    model.add_constraint(half_crown * half_crowns + shilling * shillings + sixpence * sixpences == total_value)

    # He was given 15 coins in all.
    model.add_constraint(half_crowns + shillings + sixpences == total_coins)

    return model, {"half_crowns": half_crowns}


if __name__ == "__main__":
    model, outputs = create_model({})
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
