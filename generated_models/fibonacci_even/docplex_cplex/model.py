# fibonacci_even: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python fibonacci_even.py

from docplex.mp.model import Model


def create_model(instance):
    """The Fibonacci sequence starts with 1 and 2, and each new term is the sum of the previous
    two. Find the sum of the even-valued terms that do not exceed four million."""
    limit = 4000000  # the even terms to add do not exceed four million
    # The sequence is modelled up to its term F(35) = 9 227 465. The terms up to the limit end at
    # F(33) = 3 524 578, and F(34) = 5 702 887 is already above it, so no counted term is missing.
    n = 35
    f_max = 10000000  # an upper bound on every term modelled, F(35) = 9 227 465
    res_max = 100000000  # an upper bound on the sum: all terms up to F(35) add up to 24 157 816
    terms = range(1, n + 1)

    model = Model("fibonacci_even")
    # The product below uses a bound of 10^7; with CPLEX's default integrality tolerance
    # (1e-5) a "zero" binary could carry up to 100 through it, so integrality is exact.
    model.parameters.mip.tolerances.integrality = 0

    # f[i] is the i-th term of 1, 1, 2, 3, 5, ...; f[0] = 0 only starts the recurrence, and the
    # leading 1 that the statement leaves out is odd, so it does not change the sum.
    f = [model.integer_var(0, f_max, name=f"f_{i}") for i in range(n + 1)]
    model.add_constraint(f[0] == 0)
    model.add_constraint(f[1] == 1)
    model.add_constraint(f[2] == 1)
    model.add_constraints(f[i] == f[i - 1] + f[i - 2] for i in range(3, n + 1))

    # x[i] is 1 exactly when f[i] is even and does not exceed four million.
    res_terms = []
    for i in terms:
        # f[i] = 2 * half + odd: odd is 1 when f[i] is odd.
        half = model.integer_var(0, f_max // 2, name=f"half_{i}")
        odd = model.binary_var(name=f"odd_{i}")
        model.add_constraint(f[i] == 2 * half + odd)
        # below is 1 exactly when f[i] does not exceed the limit.
        below = model.binary_var(name=f"below_{i}")
        model.add_equivalence(below, f[i] <= limit)
        # x = (not odd) and below.
        x = model.binary_var(name=f"x_{i}")
        model.add_constraint(x <= 1 - odd)
        model.add_constraint(x <= below)
        model.add_constraint(x >= below - odd)
        # counted = x * f[i]: the term if it is counted, else 0 (binary times bounded integer).
        counted = model.integer_var(0, f_max, name=f"counted_{i}")
        model.add_constraint(counted <= f_max * x)
        model.add_constraint(counted <= f[i])
        model.add_constraint(counted >= f[i] - f_max * (1 - x))
        res_terms.append(counted)

    # res is the sum of the counted terms.
    res = model.integer_var(0, res_max, name="res")
    model.add_constraint(res == model.sum(res_terms))

    return model, {"res": res}


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
