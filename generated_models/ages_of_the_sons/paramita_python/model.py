# ages_of_the_sons: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python ages_of_the_sons.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def create_model(instance):
    """The product of three sons' ages is 36. Learning the sum of their ages does not
    settle them, but learning that the oldest son is unique does. Find the ages of
    the three sons, oldest first."""
    product = 36  # the product of the three ages

    divisors = [d for d in range(1, product + 1) if product % d == 0]  # the divisors of the product
    # The possible triples of ages, oldest first, that multiply to the product.
    cands = [(x, y, z) for x in divisors for y in divisors for z in divisors
             if x >= y >= z and x * y * z == product]
    # total[i] is the sum of the ages in candidate i.
    total = {i: c[0] + c[1] + c[2] for i, c in enumerate(cands)}

    # sons[i] is true when the sons' ages are candidate i.
    sons = {i: Bool(f"sons_are_candidate_{i}") for i in range(len(cands))}
    # other[i] is true when candidate i is a second possibility with the same sum.
    other = {i: Bool(f"other_candidate_{i}") for i in range(len(cands))}

    # The sons' ages are one candidate.
    constraints = [sum(sons.values()) == 1]
    # The mathematician cannot tell the ages from their sum alone, so a second
    # possibility with the same sum exists.
    constraints.append(sum(other.values()) == 1)
    for i in range(len(cands)):
        # The second possibility is a different triple.
        constraints.append(~(sons[i] & other[i]))
        # The second possibility has the same sum as the sons' ages.
        for j in range(len(cands)):
            if total[i] != total[j]:
                constraints.append(If(sons[i], ~other[j]))

    # The oldest son is unique, so the two eldest are not the same age.
    for i, (x, y, _) in enumerate(cands):
        if x == y:
            constraints.append(~sons[i])

    # Candidate j, with a unique oldest son, is the sons' ages whenever the sons' sum
    # is the sum of j.
    for j, (x, y, _) in enumerate(cands):
        if x == y:
            continue
        # The candidates with the same sum as j.
        same_sum = [sons[k] for k in range(len(cands)) if total[k] == total[j]]
        constraints.append(If(Or(same_sum), sons[j]))

    a1 = sum(c[0] * sons[i] for i, c in enumerate(cands))  # the oldest son's age
    a2 = sum(c[1] * sons[i] for i, c in enumerate(cands))  # the middle son's age
    a3 = sum(c[2] * sons[i] for i, c in enumerate(cands))  # the youngest son's age

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"A1": a1, "A2": a2, "A3": a3}


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
