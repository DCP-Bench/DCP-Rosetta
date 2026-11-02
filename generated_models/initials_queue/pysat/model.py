# initials_queue: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python initials_queue.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Ten people stand in a queue. Each has two distinct initials from A to E in
    alphabetical order, nobody has the same initials as another person, and nobody shares
    a letter with the person in front. BE is at the front, CD right behind, and BD at the
    end. What are the initials of the ten people, from the front?"""
    n_people = 10  # people in the queue
    n_letters = 5  # the letters A to E, numbered 0 to 4

    pool = IDPool()

    # queue[i][k] is the k-th initial of the person at place i, counting from the front
    queue = [[Integer(f"queue_{i}_{k}", 0, n_letters - 1, vpool=pool) for k in range(2)]
             for i in range(n_people)]
    engine = IntegerEngine(vars=[v for row in queue for v in row], vpool=pool)
    formula = engine.clausify()

    # The two initials of each person are in alphabetical order and different.
    for i in range(n_people):
        for a in range(n_letters):
            for b in range(a + 1):
                formula.append([-queue[i][0].equals(a), -queue[i][1].equals(b)])

    # Nobody has the same initials as another person.
    for i in range(n_people):
        for j in range(i + 1, n_people):
            for a in range(n_letters):
                for b in range(n_letters):
                    formula.append([-queue[i][0].equals(a), -queue[i][1].equals(b),
                                    -queue[j][0].equals(a), -queue[j][1].equals(b)])

    # Nobody shares a letter with the person in front of them.
    for i in range(n_people - 1):
        for k in range(2):
            for m in range(2):
                for a in range(n_letters):
                    formula.append([-queue[i][k].equals(a), -queue[i + 1][m].equals(a)])

    # BE is at the front, CD right behind, and BD at the end of the queue.
    for i, (first, second) in ((0, (1, 4)), (1, (2, 3)), (n_people - 1, (1, 3))):
        formula.append([queue[i][0].equals(first)])
        formula.append([queue[i][1].equals(second)])

    return formula, {"queue": queue}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
