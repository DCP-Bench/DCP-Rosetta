# allergy: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python allergy.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, add_to_container, to_cnf


def create_model(instance):
    """Four friends are each allergic to something different (eggs, mold, nuts,
    ragweed) and have a different surname (Baxter, Lemon, Malone, Fleet). Match
    each allergy and each surname to a friend, given the clues."""
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]
    # The four friends are numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    friends = range(4)
    debra, janet, hugh, rick = friends

    # allergic[f][p] is true when friend p is allergic to food f.
    allergic = {f: [Bool(f"allergic_{f}_{p}") for p in friends] for f in foods}
    # has_surname[s][p] is true when friend p has surname s.
    has_surname = {s: [Bool(f"has_surname_{s}_{p}") for p in friends] for s in surnames}

    # The constraints of the puzzle.
    constraints = []

    # Each food is the allergy of exactly one friend.
    constraints += [sum(allergic[f]) == 1 for f in foods]
    # Each friend has exactly one allergy.
    constraints += [sum(allergic[f][p] for f in foods) == 1 for p in friends]

    # Each surname belongs to exactly one friend.
    constraints += [sum(has_surname[s]) == 1 for s in surnames]
    # Each friend has exactly one surname.
    constraints += [sum(has_surname[s][p] for s in surnames) == 1 for p in friends]

    # Rick is not allergic to mold.
    constraints.append(~allergic["mold"][rick])

    # Whoever is surnamed Baxter is the one allergic to eggs.
    constraints += [Iff(has_surname["baxter"][p], allergic["eggs"][p]) for p in friends]

    # Hugh is neither surnamed Lemon nor Fleet.
    constraints.append(~has_surname["lemon"][hugh])
    constraints.append(~has_surname["fleet"][hugh])

    # Debra is allergic to ragweed.
    constraints.append(allergic["ragweed"][debra])

    # Janet is not surnamed Lemon, and is allergic to neither eggs nor mold.
    constraints.append(~has_surname["lemon"][janet])
    constraints.append(~allergic["eggs"][janet])
    constraints.append(~allergic["mold"][janet])

    # Each food and surname maps to the number of the friend who has it.
    outputs = {f: sum(p * allergic[f][p] for p in friends) for f in foods}
    outputs.update({s: sum(p * has_surname[s][p] for p in friends) for s in surnames})

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


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
