# diet: a Paramita (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python diet.py diet.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf

# Nutrition table of the problem. NUTRIENTS[k][j] is the amount of nutrient k in one
# portion of food j.
# Rows: calories, chocolate (ounces), sugar (ounces), fat (ounces).
# Columns: chocolate cake, chocolate ice cream, cola, pineapple cheesecake.
NUTRIENTS = [
    [400, 200, 150, 500],  # calories
    [3, 2, 0, 0],          # chocolate (ounces)
    [2, 2, 4, 4],          # sugar (ounces)
    [2, 4, 1, 5],          # fat (ounces)
]


def create_model(instance):
    """Choose how many portions of four foods to eat so that the diet contains at
    least the minimum of each nutrient, at the lowest cost."""
    n = instance["n"]            # the number of foods
    price = instance["price"]    # price[j]: the price of one portion of food j
    limits = instance["limits"]  # limits[k]: the least amount of nutrient k the diet must contain
    assert len(price) == n and len(NUTRIENTS[0]) == n

    # A cheapest diet never needs more than max_portions[j] portions of food j, since
    # a portion beyond that can be left out without losing a nutrient.
    max_portions = []
    for j in range(n):
        bounds = [-(-limits[k] // NUTRIENTS[k][j]) for k in range(len(limits)) if NUTRIENTS[k][j] > 0]
        max_portions.append(max(bounds, default=0))

    # units[j][v] is true when at least v+1 portions of food j are bought
    units = [[Bool(f"units_{j}_ge_{v + 1}") for v in range(max_portions[j])] for j in range(n)]

    cons = []
    # Buying v+1 portions of a food requires v portions of it.
    for j in range(n):
        for v in range(1, max_portions[j]):
            cons.append(If(units[j][v], units[j][v - 1]))

    # Each nutrient reaches its minimum over all portions bought.
    for k in range(len(limits)):
        amount = sum(NUTRIENTS[k][j] * b for j in range(n) for b in units[j])
        if isinstance(amount, int):
            # No food has this nutrient, or no portion is allowed, so the minimum must be 0.
            assert limits[k] <= 0
            continue
        cons.append(amount >= limits[k])

    # The price of the portions bought.
    cost = sum(price[j] * b for j in range(n) for b in units[j])

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-cost, And(cons), to_cnf, formula, pool)

    return (formula, pool), {"cost": cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

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
