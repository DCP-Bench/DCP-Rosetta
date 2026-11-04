# handshaking: a Paramita (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python handshaking.py handshaking.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples for dinner. Everybody
    shakes hands with some of the others, but nobody shakes hands with themselves or
    with their spouse. Jocelyn asks everyone except herself how many hands they have
    shaken, and all the answers are different. How many hands has Hilary shaken?"""
    num_couples = instance["num_couples"]  # the number of invited couples
    # Hilary and Jocelyn are persons 0 and 1. Persons 2k and 2k + 1 are married.
    n_people = 2 * (num_couples + 1)
    max_hands = n_people - 2  # everyone except themselves and their spouse

    # The spouse of person p.
    def spouse(p):
        return p ^ 1

    # shake[(i, j)] is true when persons i and j, i < j, shake hands. A person does not
    # shake hands with themselves or their spouse, so those pairs have no variable.
    shake = {}
    for i in range(n_people):
        for j in range(i + 1, n_people):
            if j != spouse(i):
                shake[(i, j)] = Bool(f"shake_{i}_{j}")

    # The number of hands person p has shaken.
    def hands(p):
        return sum(shake[(min(p, q), max(p, q))]
                   for q in range(n_people) if q != p and q != spouse(p))

    # Jocelyn asks everyone else. answer[p][v] is true when person p answers v.
    asked = [p for p in range(n_people) if p != 1]
    answer = {p: {v: Bool(f"hands_{p}_is_{v}") for v in range(max_hands + 1)} for p in asked}

    constraints = []

    # Each person gives exactly one answer, and it is the number of hands they shook.
    for p in asked:
        constraints.append(sum(answer[p].values()) == 1)
        constraints.append(hands(p) == sum(v * answer[p][v] for v in range(max_hands + 1)))

    # All answers are different. There are as many people asked as possible answers, so
    # each possible number of hands is given to exactly one of them.
    for v in range(max_hands + 1):
        constraints.append(sum(answer[p][v] for p in asked) == 1)

    # The number of hands Hilary has shaken.
    hil = hands(0)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"hil": hil}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

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
