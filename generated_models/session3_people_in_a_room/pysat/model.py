# session3_people_in_a_room: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python session3_people_in_a_room.py

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an entry order
    such that the ratio of females to males in the room is never above 7/3."""
    # The problem fixes its own data, so the instance is not read.
    total_people = 13  # the number of people entering the room
    num_males = 4      # how many of them are male

    pool = IDPool()
    # sequence[i] is true when the i-th person to enter is a woman
    sequence = [pool.id(("p", i)) for i in range(total_people)]

    cnf = CNF()
    # Exactly 4 of the 13 people are men, so 9 are women.
    cnf.extend(CardEnc.equals(lits=sequence, bound=total_people - num_males,
                              vpool=pool, encoding=EncType.seqcounter).clauses)

    # After i entries, women / men <= 7 / 3, i.e. 3 * women <= 7 * men. With men = i - women
    # this is 10 * women <= 7 * i. An empty room has no ratio, so the count starts at 1.
    for i in range(1, total_people):
        cnf.extend(PBEnc.leq(lits=sequence[:i], weights=[10] * i, bound=7 * i,
                             vpool=pool).clauses)

    return cnf, {"sequence": sequence}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

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
