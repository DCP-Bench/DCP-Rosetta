# fibonacci_even: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python fibonacci_even.py

from pycsp3 import *


def create_model(instance):
    """Each new term in the Fibonacci sequence is the sum of the previous two terms,
    starting with 1 and 2. Find the sum of the even-valued terms that do not exceed
    four million."""
    limit = 4_000_000  # the bound on the terms that are counted
    first_term = 1  # the first term of the sequence
    second_term = 2  # the second term of the sequence

    # The terms of the sequence that do not exceed the limit, in order. The terms are listed
    # here in Python to give each term a small domain: the domain range(limit + 1) for every
    # term would exceed ACE's domain-size budget. Terms above the limit are never counted, so
    # the list stops at the last term that does not exceed it. The recurrence below still
    # constrains each term, but the domains alone restrict it to Fibonacci numbers.
    terms = [first_term, second_term]
    while terms[-1] + terms[-2] <= limit:
        terms.append(terms[-1] + terms[-2])
    n_terms = len(terms)

    # term[k] is the (k + 1)-th term of the sequence
    term = VarArray(size=n_terms, dom=terms)

    # even[k] is 1 when term k is even
    even = VarArray(size=n_terms, dom={0, 1})

    # res is the sum of the even-valued terms. The terms are positive, so res is at most the
    # sum of all the terms.
    res = Var(dom=range(sum(terms) + 1))

    satisfy(
        # The sequence starts with 1 and 2.
        term[0] == first_term,
        term[1] == second_term,
        # Each term is the sum of the previous two.
        [term[k] == term[k - 1] + term[k - 2] for k in range(2, n_terms)],
        # even[k] is 1 exactly when term k is even.
        [even[k] == (term[k] % 2 == 0) for k in range(n_terms)],
        # res is the sum of the even-valued terms.
        res == Sum(term[k] * even[k] for k in range(n_terms)),
    )

    return {"res": res}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
