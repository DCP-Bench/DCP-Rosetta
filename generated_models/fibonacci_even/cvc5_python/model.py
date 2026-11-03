# fibonacci_even: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install cvc5 numpy`) with:
#   python fibonacci_even.py

import cvc5.pythonic as c5


def create_model(instance):
    """Each new term of the sequence starting with 1 and 2 is the sum of the previous
    two. Find the sum of the even terms that do not exceed four million."""
    limit = 4000000  # the largest term that is counted
    # how many terms are listed; the 32nd, 3524578, is the last one not above the limit
    n_terms = 40

    # terms[i] is the (i+1)-th term of the sequence
    terms = [c5.Int(f"term_{i}") for i in range(n_terms)]
    # res is the sum of the even terms that do not exceed the limit
    res = c5.Int("res")

    solver = c5.Solver()

    # The first two terms are 1 and 2, and each later term is the sum of the previous two.
    solver.add(terms[0] == 1, terms[1] == 2)
    solver.add([terms[i] == terms[i - 1] + terms[i - 2] for i in range(2, n_terms)])

    # res adds up the even terms that do not exceed the limit.
    solver.add(
        res == c5.Sum([c5.If(c5.And(t <= limit, t % 2 == 0), t, 0) for t in terms])
    )

    return solver, {"res": res}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
