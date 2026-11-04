# twelve_pack: a hermax (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install hermax`):
#   python twelve_pack.py twelve_pack.json

from hermax.model import Model


def create_model(instance):
    """Given a target number of items, choose how many packs of each size to buy so
    that the packs together meet or exceed the target, and the number of items bought
    is as close to the target as possible (fewest items above it).

    Report the number of packs of each size bought."""
    packs = instance["packs"]    # packs[i]: the number of items in pack size i
    target = instance["target"]  # target: the number of items wanted
    n = len(packs)               # n: the number of pack sizes
    largest = max(packs)         # the largest pack size on offer

    m = Model()

    # counts[i] is how many packs of size packs[i] are bought. Buying more than
    # target // packs[i] + 1 packs of one size is never needed, because the
    # target would already be met without the last one.
    counts = [m.int(f"count_{i}", 0, target // packs[i] + 1) for i in range(n)]

    # excess is how many items the packs bought hold above the target.
    # Buying only packs of the largest size meets the target with fewer than
    # `largest` items above it, so an optimal purchase never has more excess than that.
    excess = m.int("excess", 0, largest - 1)

    # The packs bought together hold the target number of items plus the excess.
    m &= (sum(packs[i] * counts[i] for i in range(n)) == target + excess)

    # Minimise the excess: the fewest items above the target. The target itself is
    # fixed, so this is the same choice as minimising the items bought, but over a
    # small range, which keeps the soft clauses small.
    m.obj += excess

    return m, {"counts": counts}


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
