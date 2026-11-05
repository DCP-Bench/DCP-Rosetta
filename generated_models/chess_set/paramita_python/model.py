# chess_set: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python chess_set.py

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def unary_count(name, ub):
    # ge[k] is true when at least k + 1 sets of this kind are made, for k < ub
    ge = [Bool(f"{name}_ge_{k + 1}") for k in range(ub)]
    # making k + 1 sets means making k sets too
    chain = [If(ge[k + 1], ge[k]) for k in range(ub - 1)]
    return ge, chain


def create_model(instance):
    """A joinery makes small and large boxwood chess sets each week, within its lathe hours and
    boxwood, so as to maximise its profit."""
    lathe_hours = 4 * 40                 # four lathes, 40 hours each a week
    boxwood_kg = 200                     # boxwood available a week
    small_lathe, large_lathe = 3, 2      # lathe hours per small / large set
    small_wood, large_wood = 1, 3        # kg of boxwood per small / large set
    small_profit, large_profit = 5, 20   # profit per small / large set

    # the most sets of each kind that the lathe hours or the boxwood allow on their own
    small_max = min(lathe_hours // small_lathe, boxwood_kg // small_wood)
    large_max = min(lathe_hours // large_lathe, boxwood_kg // large_wood)

    small_ge, small_chain = unary_count("small", small_max)
    large_ge, large_chain = unary_count("large", large_max)
    constraints = small_chain + large_chain
    small = sum(small_ge)  # the number of small sets made
    large = sum(large_ge)  # the number of large sets made

    # The lathe hours used do not exceed the lathe hours available.
    constraints.append(small_lathe * small + large_lathe * large <= lathe_hours)
    # The boxwood used does not exceed the boxwood available.
    constraints.append(small_wood * small + large_wood * large <= boxwood_kg)

    # The profit from the sets made, to be maximised.
    profit = small_profit * small + large_profit * large

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(profit, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the profit, maximised (the soft clauses
    # maximise it).
    return (formula, pool), {"small_set": small, "large_set": large, "max_profit": profit}, profit


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
