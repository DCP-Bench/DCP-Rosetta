# fibonacci_even: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install pychoco numpy`) with:
#   python fibonacci_even.py

from pychoco.model import Model


def create_model(instance):
    """Each new term in the Fibonacci sequence is the sum of the previous two,
    starting from 0 and 1. Find the sum of the even-valued terms that do not
    exceed four million."""
    # Enough terms to go past four million; the 35th term is 9227465.
    n_terms = 35
    # The limit on a counted term: four million.
    limit = 4000000
    # Bound on every term, well above the limit.
    max_term = 10000000
    # Bound on the sum of the counted terms.
    max_sum = 100000000

    model = Model()

    # f[i] is the i-th term of the sequence; the first three are 0, 1, 1
    f = [model.intvar(0, 0, name="f_0"), model.intvar(1, 1, name="f_1"), model.intvar(1, 1, name="f_2")]
    for i in range(3, n_terms + 1):
        f.append(model.intvar(0, max_term, name=f"f_{i}", bounded_domain=True))

    # Each later term is the sum of the previous two.
    for i in range(3, n_terms + 1):
        model.sum([f[i - 1], f[i - 2]], "=", f[i]).post()

    # zero is what a term that is not counted contributes.
    zero = model.intvar(0, 0, name="zero")
    # contributions[i] is the part of term i that goes into the sum
    contributions = []
    for i in range(1, n_terms + 1):
        # half is the term halved, rounded down, and odd is true when the term is odd;
        # together they give the term
        half = model.intvar(0, max_term // 2, name=f"half_{i}", bounded_domain=True)
        odd = model.boolvar(name=f"odd_{i}")
        model.scalar([f[i], half, odd], [1, -2, -1], "=", 0).post()

        # small is true when the term is under four million; no term equals it
        small = model.arithm(f[i], "<", limit).reify()
        # counted[i] is true when the term is even and small, so it goes into the sum
        counted = model.boolvar(name=f"counted_{i}")
        model.arithm(counted, "<=", small).post()
        model.arithm(counted, "+", odd, "<=", 1).post()
        model.scalar([counted, small, odd], [1, -1, 1], ">=", 0).post()

        # The term itself when counted, zero otherwise.
        contribution = model.intvar(0, max_term, name=f"contribution_{i}", bounded_domain=True)
        model.element(contribution, [zero, f[i]], counted).post()
        contributions.append(contribution)

    # res is the sum of the even terms below four million.
    res = model.intvar(0, max_sum, name="res", bounded_domain=True)
    model.sum(contributions, "=", res).post()

    return model, {"res": res}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
