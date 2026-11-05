# equal_sized_groups: a Paramita (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python equal_sized_groups.py equal_sized_groups.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, Or, add_to_weighted_container, to_cnf


def create_model(instance):
    """Divide a sorted list of n elements into k groups by choosing k-1 split points,
    keeping elements with the same value in the same group, with the groups as close
    in size to round(n/k) as possible. Find the split points that minimise the total
    error."""
    a = instance["a"]  # the sorted elements
    k = instance["k"]  # the number of groups
    n = len(a)  # the number of elements
    ideal = round(n / k)  # the group size to aim for, round(n/k)

    # n_bits is the number of powers of two needed to reach any position up to n
    n_bits = max(1, n.bit_length())
    # pos_bits[j][b] is true when the position of split j includes 2**b
    pos_bits = {j: [Bool(f"split_{j}_bit_{b}") for b in range(n_bits)] for j in range(1, k)}
    # pos[j] is the 1-based index of the last element of group j, the element before split j
    pos = {j: sum(2 ** b * pos_bits[j][b] for b in range(n_bits)) for j in range(1, k)}

    # max_err is the largest error a group can have. A group has between 1 and n - k + 1 elements.
    max_err = max(ideal - 1, n - k + 1 - ideal, 0)
    n_err_bits = max(1, max_err.bit_length())
    # err_bits[j][q] is true when the error of group j includes 2**q
    err_bits = {j: [Bool(f"err_{j}_bit_{q}") for q in range(n_err_bits)] for j in range(1, k + 1)}
    # err[j] is the error of group j, how far its size is from the ideal size
    err = {j: sum(2 ** q * err_bits[j][q] for q in range(n_err_bits)) for j in range(1, k + 1)}

    # size_terms(j) gives the size of group j as weighted Bools plus a constant: the position
    # of split j minus the position of split j-1, where split 0 is at 0 and split k is at n.
    def size_terms(j):
        terms = []
        if j <= k - 1:
            terms += [(2 ** b, pos_bits[j][b]) for b in range(n_bits)]
        if j >= 2:
            terms += [(-(2 ** b), pos_bits[j - 1][b]) for b in range(n_bits)]
        const = n if j == k else 0
        return terms, const

    constraints = []

    # Each split point is after the first element and before the last one.
    for j in range(1, k):
        constraints += [pos[j] >= 1, pos[j] <= n - 1]

    # Each split point is at least one element after the previous one, so no group is empty.
    for j in range(2, k):
        constraints.append(pos[j] - pos[j - 1] >= 1)

    # No split point falls between two equal neighbouring elements.
    for j in range(1, k):
        for i in range(1, n):
            if a[i - 1] == a[i]:
                constraints.append(
                    Or([~bit if (i >> b) & 1 else bit for b, bit in enumerate(pos_bits[j])])
                )

    # Each error is at least the gap between its group size and the ideal size, in either direction.
    for j in range(1, k + 1):
        terms, const = size_terms(j)
        constraints.append(sum(c * b for c, b in terms) - err[j] <= ideal - const)
        constraints.append(-sum(c * b for c, b in terms) - err[j] <= -ideal + const)

    # The total error is the sum of the group errors, and it is minimised.
    total_error = sum(err[j] for j in range(1, k + 1))

    # x holds the split points, from the first group to the one before the last.
    x = [pos[j] for j in range(1, k)]

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_error, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total error, the sum over the groups of
    # how far each size is from the ideal size, minimised (its negation is what the soft
    # clauses maximise).
    return (formula, pool), {"x": x}, total_error


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

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
