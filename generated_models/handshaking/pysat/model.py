# handshaking: a PySAT (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python handshaking.py handshaking.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples. Everybody shakes hands
    with some of the others, but nobody with themselves or their spouse. Everybody
    except Hilary has shaken a different number of hands. How many hands has Hilary
    shaken?"""
    n_couples = instance["num_couples"]  # the invited couples, not counting Hilary and Jocelyn
    n_people = 2 + 2 * n_couples

    # Person 0 is Hilary and person 1 is Jocelyn. The invited couples are the pairs
    # (2, 3), (4, 5), and so on, and the two people of a pair are married.
    def spouse(i):
        return i ^ 1

    pool = IDPool()
    # shake[i, j] (i < j) is true when persons i and j shake hands. A handshake is mutual,
    # so each pair has one variable. Nobody shakes hands with themselves or their spouse,
    # so those pairs have none.
    shake = {(i, j): pool.id(("shake", i, j))
             for i in range(n_people) for j in range(i + 1, n_people) if j != spouse(i)}
    # handshakes[i]: the handshakes that person i could have.
    handshakes = [[shake[min(i, j), max(i, j)] for j in range(n_people) if j != i and j != spouse(i)]
                  for i in range(n_people)]

    # count[i] is the number of hands person i has shaken, from 0 up to n_people - 2,
    # since nobody shakes their own hand or their spouse's.
    count = [Integer(f"count_{i}", 0, n_people - 2, encoding="coupled", vpool=pool)
             for i in range(n_people)]
    engine = IntegerEngine(vars=count, vpool=pool)

    # Everybody except Hilary has shaken a different number of hands.
    engine.add_alldifferent(count[1:])

    # Couples can be renamed among themselves, and the two people of a couple can swap
    # places, without changing Hilary's count. So in each couple the first person has
    # shaken more hands than the second, and the first persons of the couples have
    # counts in decreasing order.
    for c in range(1, n_couples + 1):
        engine.add_linear(count[2 * c] - count[2 * c + 1] >= 1)
        if c < n_couples:
            engine.add_linear(count[2 * c] - count[2 * c + 2] >= 1)

    cnf = engine.clausify()

    # The clauses that count the handshakes of person i only bind when count[i] = v, and then
    # exactly v of person i's handshakes are true.
    for i in range(n_people):
        for v in range(n_people - 1):
            guard = -count[i].equals(v)
            for clause in CardEnc.equals(lits=handshakes[i], bound=v, vpool=pool,
                                         encoding=EncType.seqcounter).clauses:
                cnf.append([guard] + clause)

    # Each count from 0 to n_people - 2 is taken by someone other than Hilary.
    for v in range(n_people - 1):
        cnf.append([count[i].equals(v) for i in range(1, n_people)])

    return cnf, {"hil": count[0]}


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
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
