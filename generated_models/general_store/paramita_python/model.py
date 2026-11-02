# general_store: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python general_store.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf

# The words above the line.
ADDENDS = [
    "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
    "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP",
]
# The word below the line.
TOTAL = "ALLWOOL"
# The ten digits.
DIGITS = range(10)
# The columns of the sum, counted from the right. The total has one letter per column.
COLUMNS = len(TOTAL)


def create_model(instance):
    """The owner of a general store puts up a sign: the words above the line add up,
    column by column, to ALL WOOL. Each different letter stands for a different digit.
    Find the digit of every letter."""
    words = ADDENDS + [TOTAL]
    # The ten letters of the sum.
    letters = sorted({ch for w in words for ch in w})

    # stands_for[L][d] is true when letter L stands for digit d.
    stands_for = {L: {d: Bool(f"x_{L}_{d}") for d in DIGITS} for L in letters}

    # The number that letter L stands for.
    def value(L):
        return sum(d * stands_for[L][d] for d in DIGITS)

    constraints = []

    # Each letter stands for exactly one digit.
    constraints += [sum(stands_for[L].values()) == 1 for L in letters]
    # Different letters stand for different digits: each digit is taken by exactly one letter.
    constraints += [sum(stands_for[L][d] for L in letters) == 1 for d in DIGITS]

    # largest_carry[j] is the most that can be carried into column j, found column by column from the right.
    largest_carry = {0: 0}
    for j in range(COLUMNS):
        n_words_j = sum(1 for w in ADDENDS if len(w) > j)
        largest_carry[j + 1] = (9 * n_words_j + largest_carry[j]) // 10

    # carry[j] is the carry into column j. There is no carry into the first column,
    # and none out of the last, since the sum has no letter beyond ALL WOOL.
    carry = {0: 0, COLUMNS: 0}
    for j in range(1, COLUMNS):
        # carry_ge[i] is true when the carry into column j is at least i + 1.
        carry_ge = [Bool(f"carry_{j}_ge_{i + 1}") for i in range(largest_carry[j])]
        # A carry of at least i + 2 is at least i + 1.
        constraints += [If(carry_ge[i + 1], carry_ge[i]) for i in range(len(carry_ge) - 1)]
        carry[j] = sum(carry_ge)

    # Column by column from the right, the digits of the words and the carry in add up
    # to the digit of ALL WOOL plus ten times the carry out.
    for j in range(COLUMNS):
        column_digits = [value(w[-1 - j]) for w in ADDENDS if len(w) > j]
        constraints.append(sum(column_digits) + carry[j] == value(TOTAL[-1 - j]) + 10 * carry[j + 1])

    # The digit of each letter.
    outputs = {L: value(L) for L in letters}

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
