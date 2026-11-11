# csplib_044_steiner: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_044_steiner.py csplib_044_steiner.json

from pycsp3 import *


def create_model(instance):
    """The ternary Steiner problem of order n: find a set of n * (n - 1) / 6 triples of distinct
    elements of {1, ..., n} such that any two triples have at most one common element. Here n
    modulo 6 is 1 or 3."""
    n = instance["n"]                              # the order: the number of elements
    triple_size = 3                                # each triple has three distinct elements
    n_triples = n * (n - 1) // 6                   # the number of triples, as the statement gives
    # Two triples with at most one common element differ in at least 2 * (3 - 1) = 4 positions.
    min_hamming = 2 * (triple_size - 1)
    # Implied: the triples cover each of the n * (n - 1) / 2 pairs at most once, and there are exactly
    # that many pairs covered (n_triples * 3), so every pair is covered once. Element j then lies in
    # (n - 1) / 2 triples: it has n - 1 partners, and each triple containing it covers two of them.
    triples_per_element = (n - 1) // 2

    # triples[i][j] is 1 when element j is part of triple i
    triples = VarArray(size=[n_triples, n], dom={0, 1})

    satisfy(
        # Each triple has three elements.
        [Sum(triples[i]) == triple_size for i in range(n_triples)],
        # Any two triples have at most one common element.
        [Hamming(triples[i], triples[j]) >= min_hamming for i in range(n_triples) for j in range(i + 1, n_triples)],
        # Each element lies in triples_per_element triples (implied, see above).
        [Sum(triples[i][j] for i in range(n_triples)) == triples_per_element for j in range(n)],
    )

    return {"sets": triples}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("sets", "=")
        for row in outputs["sets"]:
            print(values(row))
    else:
        print("No solution:", status())
