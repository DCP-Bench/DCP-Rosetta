# cutting_stock: a hermax (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install hermax`):
#   python cutting_stock.py cutting_stock.json

from hermax.model import Model


def create_model(instance):
    """Cutting stock: raw rolls of one width are cut with a fixed set of cutting patterns,
    each pattern giving some pieces of each ordered width. Choose how many rolls to cut
    with each pattern so that every ordered width gets at least as many pieces as ordered,
    using as few raw rolls as possible."""
    num_patterns = instance["num_patterns"]          # the number of cutting patterns
    num_rolls_width = instance["num_rolls_width"]    # num_rolls_width[i][j]: pieces of width j that one roll cut with pattern i gives
    orders = instance["orders"]                      # orders[j]: how many pieces of width j are ordered
    # roll_width and widths only describe the problem: each pattern already lists its pieces per width.

    m = Model()

    # patterns_used[i] is how many raw rolls are cut with pattern i. Never more than the largest
    # order: a pattern cut that many times already makes every width it contains enough, so
    # using it more often only adds rolls.
    patterns_used = m.int_vector("patterns_used", num_patterns, 0, max(orders))

    # Each width j must get at least as many pieces as it is ordered, summed over all patterns.
    for j in range(len(orders)):
        m &= (sum(num_rolls_width[i][j] * patterns_used[i] for i in range(num_patterns)) >= orders[j])

    # The total number of raw rolls cut is the sum of the pattern counts; minimise it.
    min_rolls_cut = sum(patterns_used[i] for i in range(num_patterns))
    m.obj += min_rolls_cut

    return m, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}


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
