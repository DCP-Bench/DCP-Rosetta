# abbots_puzzle: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python abbots_puzzle.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Share 100 bushels of corn among 100 people, each man getting three bushels,
    each woman two and each child half a bushel, with five times as many women as
    men. Find the number of men, women and children."""
    n_people = 100   # the people who share the corn
    n_bushels = 100  # the bushels of corn to share

    # men[v], women[v] and children[v] are true when there are v people of that kind.
    men = {v: Bool(f"men_{v}") for v in range(n_people + 1)}
    women = {v: Bool(f"women_{v}") for v in range(n_people + 1)}
    children = {v: Bool(f"children_{v}") for v in range(n_people + 1)}

    def total(group, per_person=1):
        # The sum of per_person over the people in the group.
        return sum(per_person * v * group[v] for v in range(1, n_people + 1))

    # Each of men, women and children has exactly one number.
    constraints = [sum(men.values()) == 1,
                   sum(women.values()) == 1,
                   sum(children.values()) == 1]
    # The 100 people are the men, the women and the children.
    constraints.append(total(men) + total(women) + total(children) == n_people)
    # The shares add up to 100 bushels, which is 200 half bushels: a man gets 6 half
    # bushels, a woman 4 and a child 1.
    constraints.append(total(men, 6) + total(women, 4) + total(children, 1) == 2 * n_bushels)
    # There are five times as many women as men.
    constraints.append(total(women) == total(men, 5))

    outputs = {"children": total(children), "men": total(men), "women": total(women)}

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
