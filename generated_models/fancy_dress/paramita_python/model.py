# fancy_dress: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python fancy_dress.py

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, Or, add_to_weighted_container, to_cnf


def create_model(instance):
    """Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and pays the
    $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total cost.
    He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12."""
    # The instance has no fields: every number below is from the problem statement.
    t = Bool("t")  # he wears a green tie
    h = Bool("h")  # he wears a green hat
    r = Bool("r")  # he wears a green shirt
    s = Bool("s")  # he wears green socks
    n = Bool("n")  # he pays the entrance fee

    # Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so each
    # rule holds or he pays.
    rules = [
        # Rule 1: if someone wears a green tie he has to wear a green shirt.
        Or(If(t, r), n),
        # Rule 2: a guest who wears green socks or a green shirt must also wear a green tie
        # or a green hat.
        Or(If(s | r, t | h), n),
        # Rule 3: a guest wearing a green shirt or a green hat or who does not wear green
        # socks must wear a green tie.
        Or(If(r | h | ~s, t), n),
    ]

    # Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    cost = 10 * t + 2 * h + 12 * s + 11 * n

    # Encode into a weighted formula: the rules as hard clauses, the cost to minimise as
    # soft clauses, negated because MaxSAT maximises. The pool gives each Bool its number
    # in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-cost, And(rules), to_cnf, formula, pool)

    # The objective in the problem's terms: the total cost, minimised (its negation is what
    # the soft clauses maximise).
    return (formula, pool), {"t": t, "h": h, "r": r, "s": s, "n": n}, cost


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    (formula, pool), outputs, objective = create_model({})

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")
