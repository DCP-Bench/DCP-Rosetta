# bananas: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python bananas.py

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf

TOTAL_FRUITS = 100  # fruits to buy


def allowed_combinations():
    # Prices in 1/315 dollar, so every price is whole: a banana 189, an orange 225,
    # a mango 245, an apple 945. The 100 dollars are 31500 units. Spending the 100
    # dollars forces the oranges to come in groups of 7: with 7k oranges, m mangoes
    # and a apples, the bananas are the rest, 100 - 7k - m - a, and the money gives
    # 9k + 2m + 27a = 450.
    combos = []
    for k in range(1, 15):    # 7k oranges, leaving room for the other three kinds
        for a in range(1, 17):  # at least one apple; 27a < 450 bounds it at 16
            twice_m = 450 - 9 * k - 27 * a
            if twice_m <= 0 or twice_m % 2:
                continue
            m = twice_m // 2
            b = TOTAL_FRUITS - 7 * k - m - a
            if m >= 1 and b >= 1:  # at least one mango and one banana
                combos.append((7 * k, m, b, a))
    return combos


def create_model(instance):
    """Buy 100 fruits for exactly 100 dollars, at least one of each kind: bananas
    cost 3 dollars for 5, oranges 5 dollars for 7, mangoes 7 dollars for 9 and
    apples 9 dollars for 3. Bananas and apples are disliked, so buy as few of them
    as possible."""
    combos = allowed_combinations()

    # pick[c] is true when the purchase is the combination c = (oranges, mangoes, bananas, apples)
    pick = {c: Bool(f"combo_o{c[0]}_m{c[1]}_b{c[2]}_a{c[3]}") for c in combos}

    # The purchase is exactly one of the allowed combinations.
    constraints = [sum(pick.values()) == 1]

    # The number of each fruit in the purchase.
    oranges = sum(c[0] * v for c, v in pick.items())
    mangoes = sum(c[1] * v for c, v in pick.items())
    bananas = sum(c[2] * v for c, v in pick.items())
    apples = sum(c[3] * v for c, v in pick.items())

    # Buy as few bananas and apples as possible.
    disliked = sum((c[2] + c[3]) * v for c, v in pick.items())

    outputs = {"apples": apples, "bananas": bananas, "mangoes": mangoes, "oranges": oranges}

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-disliked, And(constraints), to_cnf, formula, pool)

    return (formula, pool), outputs


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    (formula, pool), outputs = create_model({})

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
    else:
        print("No solution")
