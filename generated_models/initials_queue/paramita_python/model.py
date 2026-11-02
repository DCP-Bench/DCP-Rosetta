# initials_queue: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python initials_queue.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf

# The ten pairs of different letters from A to E in alphabetical order. The letters
# are the numbers 0 to 4.
PAIRS = [(a, b) for a in range(5) for b in range(a + 1, 5)]


# The place of the pair of letters (a, b) in PAIRS.
def pair_index(letters):
    return PAIRS.index(tuple(letters))


def create_model(instance):
    """Ten people stand in a queue, each with two different initials from A to E in
    alphabetical order. No two people have the same initials, and the person in front
    shares no letter with the person behind. BE is at the front, CD right behind and BD
    at the end. What are the initials of the queue, from the front?"""
    n = 10  # people in the queue
    n_pairs = len(PAIRS)  # the possible pairs of initials

    # initials[i][j] is true when the person at place i has the initials PAIRS[j].
    initials = [[Bool(f"initials_{i}_{j}") for j in range(n_pairs)] for i in range(n)]

    subject_to = []  # all constraints of the queue

    # Each person has exactly one pair of initials.
    for i in range(n):
        subject_to.append(sum(initials[i]) == 1)
    # Each pair of initials belongs to exactly one person.
    for j in range(n_pairs):
        subject_to.append(sum(initials[i][j] for i in range(n)) == 1)
    # The person in front shares no letter with the person behind.
    for i in range(n - 1):
        for j in range(n_pairs):
            for l in range(n_pairs):
                if set(PAIRS[j]) & set(PAIRS[l]):
                    subject_to.append(~(initials[i][j] & initials[i + 1][l]))
    # BE is at the front of the queue.
    subject_to.append(initials[0][pair_index((1, 4))])
    # CD is right behind BE.
    subject_to.append(initials[1][pair_index((2, 3))])
    # BD is at the end of the queue.
    subject_to.append(initials[n - 1][pair_index((1, 3))])

    # queue[i] holds the two letters, as numbers 0 to 4, of the person at place i.
    queue = [[sum(PAIRS[j][0] * initials[i][j] for j in range(n_pairs)),
              sum(PAIRS[j][1] * initials[i][j] for j in range(n_pairs))]
             for i in range(n)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"queue": queue}


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
