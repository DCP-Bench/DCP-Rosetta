# session3_kidney_exchange: a PySAT (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF


def create_model(instance):
    """At a hospital, people on the waiting list for a kidney can donate to some of the
    others. Choose donations so that as many people as possible receive a kidney, where
    anyone who gives a kidney must receive one and nobody receives more than one."""
    num_people = instance["num_people"]  # the number of people, numbered 0..num_people-1
    compatible = instance["compatible"]  # compatible[i]: the people (numbered from 1) that person i can donate to
    people = range(num_people)

    pool = IDPool()
    # transplants[i][j] is true when person i donates a kidney to person j
    transplants = [[pool.id(("transplants", i, j)) for j in people] for i in people]

    formula = WCNF()
    for i in people:
        gives = transplants[i]
        receives = [transplants[k][i] for k in people]
        # Each person gives at most one kidney and receives at most one.
        formula.extend(CardEnc.atmost(lits=gives, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        formula.extend(CardEnc.atmost(lits=receives, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        # A person who gives a kidney receives one.
        for j in people:
            formula.append([-transplants[i][j]] + receives)
        # Donations go only to the people that person i is compatible with.
        for j in people:
            if j + 1 not in compatible[i]:
                formula.append([-transplants[i][j]])

    # Every compatible pair that is not matched costs 1, so the best plan makes as many
    # donations as possible.
    for i in people:
        for j in people:
            if j + 1 in compatible[i]:
                formula.append([transplants[i][j]], weight=1)

    # The objective in the problem's terms: the number of transplants (RC2's cost is the number
    # of compatible pairs not matched).
    objective = [(1, transplants[i][j]) for i in people for j in people]

    return formula, {"transplants": transplants}, objective


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
