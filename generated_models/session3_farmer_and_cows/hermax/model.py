# session3_farmer_and_cows: a hermax (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install hermax`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

from hermax.model import Model


def create_model(instance):
    """A farmer has cows numbered 1 to num_cows, and cow i gives i units of milk. He
    gives each son a fixed number of cows, so that every son gets the same total
    quantity of milk. Decide which son gets which cow."""
    num_cows = instance["num_cows"]          # the cows are numbered 1..num_cows
    num_sons = instance["num_sons"]          # the sons are numbered 0..num_sons-1
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: how many cows son s gets

    # Cow i (counting from 0) is cow number i + 1 and gives i + 1 units of milk.
    milk_per_cow = [i + 1 for i in range(num_cows)]
    # Every son gets the same share of the total milk of all cows.
    milk_per_son = sum(milk_per_cow) // num_sons

    m = Model()

    # son[i] is the son who gets cow i, a number from 0 to num_sons - 1
    son = m.int_vector("son", num_cows, 0, num_sons - 1)
    # gets[i][s] is true when cow i goes to son s; it is the same literal as son[i] == s
    gets = [[son[i] == s for s in range(num_sons)] for i in range(num_cows)]

    # Each son gets his given number of cows.
    for s in range(num_sons):
        m &= (sum(gets[i][s] for i in range(num_cows)) == cows_per_son[s])

    # Every son gets the same total milk, the sum of the numbers of his cows.
    for s in range(num_sons):
        m &= (sum(milk_per_cow[i] * gets[i][s] for i in range(num_cows)) == milk_per_son)

    # No objective: any assignment that meets the rules above is an answer.
    return m, {"cow_assignments": son}


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
