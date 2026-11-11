# twelve_pack: a PyCSP3 model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python twelve_pack.py twelve_pack.json

from pycsp3 import *


def create_model(instance):
    """Given a target number of items, find the combination of packs of different sizes whose total number of items is at least the target and as close to it as possible."""
    target = instance["target"]  # the target number of items
    packs = instance["packs"]    # packs[i] is the number of items in a pack of kind i
    n_packs = len(packs)

    # The largest count of each pack kind that an optimum can use, the ceiling of target / pack size.
    # Derived: with one pack of a kind more than this, one pack of that kind could be removed and the
    # total would still reach the target with a smaller excess, so no optimum has more.
    max_count = [(target + size - 1) // size for size in packs]

    # counts[i] is the number of packs of kind i bought, a whole number from 0 to max_count[i] inclusive.
    counts = VarArray(size=n_packs, dom=lambda i: range(max_count[i] + 1))

    # total is the number of items in the bought packs. It is a separate variable because ACE minimised the wrong
    # quantity (the number of packs) for a direct minimize(Sum(...)) over counts with non-unit coefficients.
    # Its domain holds every value the counts can reach at their largest, so no solution is lost.
    total = Var(dom=range(sum(size * top for size, top in zip(packs, max_count)) + 1))

    # The total is the sum of the items in the packs bought: packs[i] items for each of counts[i] packs.
    satisfy(total == Sum(packs[i] * counts[i] for i in range(n_packs)))

    # The bought packs hold at least the target number of items.
    satisfy(total >= target)

    # The total number of items, which is to be as small as possible: the closest total at or above the target.
    minimize(total)

    return {"counts": counts}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
