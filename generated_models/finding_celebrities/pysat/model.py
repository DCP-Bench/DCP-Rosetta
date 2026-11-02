# finding_celebrities: a PySAT (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python finding_celebrities.py finding_celebrities.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def create_model(instance):
    """At a party, a celebrity is a person that everybody knows but that only
    knows other celebrities. Find the celebrities; at least one is present."""
    graph = instance["graph"]  # graph[i][j] is 1 when person i knows person j
    n_people = len(graph)      # the number of people at the party

    pool = IDPool()
    formula = CNF()

    # celebrities[i] is true when person i is a celebrity
    celebrities = [pool.id(("celebrity", i)) for i in range(n_people)]
    # exactly[k] is true when there are exactly k celebrities, for k from 1 to n_people
    exactly = {k: pool.id(("exactly", k)) for k in range(1, n_people + 1)}

    # Exactly one of these counts holds.
    formula.extend(CardEnc.equals(lits=list(exactly.values()), bound=1, vpool=pool,
                                  encoding=EncType.pairwise).clauses)

    # When exactly[k] holds, exactly k people are celebrities.
    for k, holds in exactly.items():
        for clause in CardEnc.equals(lits=celebrities, bound=k, vpool=pool,
                                     encoding=EncType.seqcounter).clauses:
            formula.append([-holds] + clause)

    # Person i is a celebrity exactly when everybody knows i and i knows as many
    # people as there are celebrities. The graph is fixed, so both counts are known now.
    for i in range(n_people):
        known_by_everybody = sum(graph[j][i] for j in range(n_people)) == n_people
        knows = sum(graph[i])
        if known_by_everybody and 1 <= knows <= n_people:
            formula.append([-celebrities[i], exactly[knows]])
            formula.append([celebrities[i], -exactly[knows]])
        else:
            formula.append([-celebrities[i]])

    return formula, {"celebrities": celebrities}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
