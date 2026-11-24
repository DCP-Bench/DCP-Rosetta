# session3_farmer_and_cows: a PyCSP3 model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

from pycsp3 import *


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and cow k gives k units of milk.
    He has several sons and a given number of cows for each son. Distribute the cows to the
    sons so that the total milk is the same for each son."""
    num_cows = instance["num_cows"]              # the number of cows; cow k (1-based) gives k units of milk
    num_sons = instance["num_sons"]              # the number of sons
    cows_per_son = instance["cows_per_son"]      # cows_per_son[s]: the number of cows son s receives

    # cow_son[i] is the son (0-based) who gets cow i + 1.
    cow_son = VarArray(size=num_cows, dom=range(num_sons))

    # total_milk is the milk of all cows, 1 + 2 + ... + num_cows.
    total_milk = num_cows * (num_cows + 1) // 2
    # Every son gets the same share of it. The sons' milk adds up to total_milk, so a total not
    # divisible by num_sons makes the model infeasible, which is the right answer.
    milk_per_son = total_milk // num_sons

    satisfy(
        # Each son receives the number of cows given for him.
        Cardinality(cow_son, occurrences={s: cows_per_son[s] for s in range(num_sons)}),
        # The total milk of son s, the sum of the milk of the cows he receives, is the same share of the total.
        [
            Sum((i + 1) * (cow_son[i] == s) for i in range(num_cows)) == milk_per_son
            for s in range(num_sons)
        ],
    )

    return {"cow_assignments": cow_son}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
