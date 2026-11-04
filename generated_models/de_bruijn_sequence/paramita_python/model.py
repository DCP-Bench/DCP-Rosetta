# de_bruijn_sequence: a Paramita (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python de_bruijn_sequence.py de_bruijn_sequence.json

from functools import reduce

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, add_to_container, to_cnf


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of length base**n in which every string of n symbols occurs exactly
    once as a substring. Find such a sequence."""
    base = instance["base"]  # the number of symbols in the alphabet
    n = instance["n"]  # the length of the strings that must all occur
    length = base**n  # the length of the sequence, which is also the number of strings

    # symbol[p][a] is true when position p of the sequence holds symbol a
    symbol = [[Bool(f"symbol_{p}_{a}") for a in range(base)] for p in range(length)]
    constraints = []  # the rules the sequence must follow

    # Each position holds exactly one symbol.
    constraints += [sum(symbol[p]) == 1 for p in range(length)]

    # window[i][v] is true when the n symbols from position i on, wrapping around the end, spell string v.
    window = [[Bool(f"window_{i}_{v}") for v in range(length)] for i in range(length)]
    for i in range(length):
        for v in range(length):
            # the n symbols of string v: v written in base `base` with n digits, most significant first
            digits = [(v // base ** (n - 1 - j)) % base for j in range(n)]
            # each place of the window holds the symbol that string v has there
            matches = [symbol[(i + j) % length][digits[j]] for j in range(n)]
            # window[i][v] holds exactly when every place matches
            constraints.append(Iff(window[i][v], reduce(lambda a, b: a & b, matches)))

    # Each window spells exactly one string.
    constraints += [sum(window[i]) == 1 for i in range(length)]

    # Every string occurs in exactly one window.
    constraints += [sum(window[i][v] for i in range(length)) == 1 for v in range(length)]

    # the sequence, symbol by symbol
    sequence = [sum(a * symbol[p][a] for a in range(base)) for p in range(length)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"de_bruijn": sequence}


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
