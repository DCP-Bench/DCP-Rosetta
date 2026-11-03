# session1_money_change: a hermax (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install hermax`):
#   python session1_money_change.py session1_money_change.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Alice gives Bob an exact amount of change using her available coins, using as
    few coins as possible. Each coin type has a value and a limited number of coins."""
    values = instance["types_of_coins"]     # values[j]: the value of one coin of type j
    available = instance["available_coins"]  # available[j]: how many coins of type j Alice has
    amount = instance["amount"]              # the total value of change Bob must receive
    n = len(values)                          # n: the number of coin types

    m = Model()

    # counts[j] is the number of coins of type j given to Bob, between 0 and what Alice has
    counts = [m.int(f"coin_count_{j}", 0, available[j]) for j in range(n)]

    # The coins given to Bob add up to exactly the amount of change.
    m &= (sum_expr(values[j] * counts[j] for j in range(n)) == amount)

    # Minimise the number of coins given.
    m.obj += sum_expr(counts)

    return m, {"coin_counts": counts}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
