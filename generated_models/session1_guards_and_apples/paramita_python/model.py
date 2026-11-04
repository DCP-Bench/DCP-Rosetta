# session1_guards_and_apples: a Paramita (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """A boy passes a number of gates to give an apple to a girl. At each gate he
    gives the guard half of his apples plus one, always a whole number of apples,
    and has none left after giving the girl her apple."""
    num_gates = instance["num_gates"]  # how many gates, each with a guard
    width = num_gates + 2  # binary digits per apple count, enough for the most apples the boy has

    # A whole number of apples below 2 to the power width
    def apple_count(name):
        bits = [Bool(f"{name}_bit_{k}") for k in range(width)]
        return sum(2 ** k * bits[k] for k in range(width))

    # apples[i] is the number of apples the boy has before gate i. The last entry
    # is the number he has after the last gate.
    apples = [apple_count(f"apples_{i}") for i in range(num_gates + 1)]

    # half[i] is half of the apples the boy has before gate i
    half = [apple_count(f"half_{i}") for i in range(num_gates)]

    # The rules of the story.
    subject_to = []

    # The boy has no knife, so each bribe is a whole number of apples: he has an even count before each gate.
    for i in range(num_gates):
        subject_to.append(apples[i] == 2 * half[i])

    # At each gate he gives the guard half of his apples plus one, and keeps the rest.
    for i in range(num_gates):
        subject_to.append(apples[i + 1] + half[i] + 1 == apples[i])

    # After the last gate he has one apple, which he gives the girl, leaving none.
    subject_to.append(apples[num_gates] == 1)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"apples": apples}


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
