# three_coins: a CPLEX (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python three_coins.py three_coins.json

from docplex.mp.model import Model


def create_model(instance):
    """Three coins: starting from the given faces, flip exactly one coin per move so that after
    num_moves moves the coins show all heads or all tails."""
    num_moves = instance["num_moves"]  # the number of moves, each flipping one coin
    init = instance["init"]  # init[j]: the face of coin j at the start, 1 is tails, 0 is heads
    n = len(init)  # the number of coins
    coins = range(n)

    model = Model("three_coins")

    # steps[m][j] is 1 when coin j shows tails after m moves.
    steps = [[model.binary_var(name=f"coin_{j}_after_{m}") for j in coins]
             for m in range(num_moves + 1)]

    # The coins start as given.
    model.add_constraints(steps[0][j] == init[j] for j in coins)

    # Each move flips exactly one coin. flipped is 1 when coin j changes in move m, which
    # for 0/1 values is |after - before|.
    for m in range(1, num_moves + 1):
        flipped = []
        for j in coins:
            f = model.binary_var(name=f"flip_{j}_in_{m}")
            before, after = steps[m - 1][j], steps[m][j]
            model.add_constraint(f >= after - before)
            model.add_constraint(f >= before - after)
            model.add_constraint(f <= after + before)
            model.add_constraint(f <= 2 - after - before)
            flipped.append(f)
        model.add_constraint(model.sum(flipped) == 1)

    # At the end the coins are all heads or all tails: all_tails is 1 when the coins end all tails
    # (n coins showing tails) and 0 when they end all heads (none showing tails).
    all_tails = model.binary_var(name="all_tails")
    model.add_constraint(model.sum(steps[num_moves]) == n * all_tails)

    return model, {"steps": steps}


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
