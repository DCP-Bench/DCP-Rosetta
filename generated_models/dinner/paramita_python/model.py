# dinner: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python dinner.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def count_of(name, largest):
    # ge[i] is true when at least i+2 people of this group go to dinner
    return [Bool(f"{name}_ge_{i + 2}") for i in range(largest - 1)]


def create_model(instance):
    """Twenty people go out to dinner: grandparents, parents and children, with a
    bill of exactly $20. How many of each go?"""
    # Costs are in half dollars, so the $0.50 of a child is a whole number: a
    # grandparent costs 6 half dollars ($3), a parent 4 ($2) and a child 1 ($0.50).
    # The bill of $20 is 40 half dollars.

    gs = count_of("gp", 6)   # grandparents, 1 to 6
    ps = count_of("par", 10)  # parents, 1 to 10
    cs = count_of("ch", 40)   # children, 1 to 40

    cons = []
    # A group of k+1 or more people also has k or more people.
    for bits in (gs, ps, cs):
        for i in range(len(bits) - 1):
            cons.append(If(bits[i + 1], bits[i]))

    # Each group has at least one person, plus one for each step its count reaches.
    grandparents = sum(gs) + 1
    parents = sum(ps) + 1
    children = sum(cs) + 1

    # Twenty people in total.
    cons.append(grandparents + parents + children == 20)
    # The bill is 40 half dollars.
    cons.append(6 * grandparents + 4 * parents + children == 40)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"grandparents": grandparents, "parents": parents, "children": children}


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
