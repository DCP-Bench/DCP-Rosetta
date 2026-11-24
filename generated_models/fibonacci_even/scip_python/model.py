# fibonacci_even: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python fibonacci_even.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Each new term of the Fibonacci sequence is the sum of the previous two terms.
    Starting with 1 and 2, the sequence's even-valued terms that do not exceed four
    million are added up. The instance file is empty ([]), so the statement fixes
    every value and the model does not read the instance argument."""
    LIMIT = 4_000_000  # the largest value a term may take, from the statement
    # The first two terms are 1 and 2, and each later term is the sum of the two before it,
    # so term n is the Fibonacci number F(n + 1) with F(1) = F(2) = 1. Term 32 is F(33) = 3524578,
    # and term 33 is F(34) = 5702887, which exceeds the limit; the sequence only grows, so no later
    # term fits either. The 32 terms modelled here are therefore all the terms that do not exceed the limit.
    N = 32

    model = Model("fibonacci_even")

    # term[k] is the (k + 1)-th term of the sequence, from 1 to the limit
    term = [model.addVar(f"term_{k}", vtype="I", lb=1, ub=LIMIT) for k in range(N)]
    # The sequence starts with 1 and 2
    model.addCons(term[0] == 1)
    model.addCons(term[1] == 2)
    # Each term from the third on is the sum of the two terms before it
    for k in range(2, N):
        model.addCons(term[k] == term[k - 1] + term[k - 2])

    # odd[k] is 1 when term k is odd, and 0 when it is even
    odd = [model.addVar(f"odd_{k}", vtype="B") for k in range(N)]
    # half[k] is a whole number with term[k] == 2 * half[k] + odd[k]; with odd[k] binary this
    # makes odd[k] the parity of term[k]. Its upper bound is LIMIT // 2 because term[k] <= LIMIT.
    half = [model.addVar(f"half_{k}", vtype="I", lb=0, ub=LIMIT // 2) for k in range(N)]
    for k in range(N):
        model.addCons(term[k] == 2 * half[k] + odd[k])

    # even_value[k] is term k when term k is even, and 0 when it is odd.
    # SCIP's indicators take one inequality each, so each conditional equality is two indicators, one per side.
    even_value = [model.addVar(f"even_value_{k}", vtype="I", lb=0, ub=LIMIT) for k in range(N)]
    for k in range(N):
        # when term k is even (odd[k] == 0): even_value[k] equals term[k]
        model.addConsIndicator(even_value[k] - term[k] <= 0, binvar=odd[k], activeone=False)
        model.addConsIndicator(even_value[k] - term[k] >= 0, binvar=odd[k], activeone=False)
        # when term k is odd (odd[k] == 1): even_value[k] is 0
        model.addConsIndicator(even_value[k] <= 0, binvar=odd[k])

    # The output res is the sum of the even-valued terms that do not exceed the limit
    res = quicksum(even_value)
    return model, {"res": res}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
