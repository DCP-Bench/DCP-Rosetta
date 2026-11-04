# session1_thick_as_thieves: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session1_thick_as_thieves.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Iff, Or, add_to_container, to_cnf


def create_model(instance):
    """Six suspects, at most two of them guilty: the innocent tell the truth
    and the guilty lie. Who is guilty?"""
    # guilty[name] is true when that suspect took part in the robbery
    guilty = {name: Bool(f"guilty_{name}") for name in ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]}
    n_guilty = sum(guilty.values())  # the number of guilty suspects

    subject_to = [
        # The getaway car was barely big enough to hold two.
        n_guilty <= 2,
        # The guilty one or ones: at least one suspect is guilty.
        n_guilty >= 1,
    ]

    # Innocent suspects tell the truth and guilty ones lie, so a suspect is innocent exactly when the statement is true.
    subject_to += [
        # Artie: "It wasn't me."
        Iff(~guilty["artie"], ~guilty["artie"]),
        # Bill: "Crackitt was in it up to his neck."
        Iff(~guilty["bill"], guilty["crackitt"]),
        # Crackitt: "No I wasn't."
        Iff(~guilty["crackitt"], ~guilty["crackitt"]),
        # Dodgy: "If Crackitt did it, Bill did it with him."
        Iff(~guilty["dodgy"], If(guilty["crackitt"], guilty["bill"])),
        # Edgy: "Nobody did it alone."
        Iff(~guilty["edgy"], Or(n_guilty >= 2, n_guilty == 0)),
        # Fingers: "That's right: it was Artie and Dodgy together."
        Iff(~guilty["fingers"], guilty["artie"] & guilty["dodgy"] & (n_guilty == 2)),
    ]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), guilty


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
