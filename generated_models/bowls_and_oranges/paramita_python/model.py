# bowls_and_oranges: a Paramita (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python bowls_and_oranges.py bowls_and_oranges.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, Or, add_to_container, to_cnf


def create_model(instance):
    """n bowls stand in a line at intervals of one metre, numbered 1 to n. Place all the oranges
    in the bowls, at most one orange per bowl, so that no three oranges A, B and C have the
    distance from A to B equal to the distance from B to C."""
    n_bowls = instance["n"]    # the number of bowls, numbered 1 to n along the line
    n_oranges = instance["m"]  # the number of oranges
    bowls = range(1, n_bowls + 1)

    # in_bowl[k][i] is true when orange k is in bowl i; oranges are numbered from left to right
    in_bowl = [{i: Bool(f"orange_{k}_in_bowl_{i}") for i in bowls} for k in range(n_oranges)]
    # occupied[i] is true when bowl i holds an orange
    occupied = {i: Bool(f"bowl_{i}_has_orange") for i in bowls}

    cons = []   # all constraints of the placement

    # Each orange is in exactly one bowl.
    cons += [sum(in_bowl[k].values()) == 1 for k in range(n_oranges)]

    # A bowl is occupied exactly when some orange is in it.
    cons += [Iff(occupied[i], Or([in_bowl[k][i] for k in range(n_oranges)])) for i in bowls]

    # bowl_of[k] is the bowl that orange k is in.
    bowl_of = [sum(i * in_bowl[k][i] for i in bowls) for k in range(n_oranges)]

    # Each orange lies in a later bowl than the orange before it, so no bowl holds two oranges.
    cons += [bowl_of[k] + 1 <= bowl_of[k + 1] for k in range(n_oranges - 1)]

    # No three bowls i, i + d and i + 2d, spaced evenly, all hold an orange.
    for i in bowls:
        for d in range(1, n_bowls):
            if i + 2 * d > n_bowls:
                break
            cons.append(~(occupied[i] & occupied[i + d] & occupied[i + 2 * d]))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": bowl_of}


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
