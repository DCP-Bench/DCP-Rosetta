# session2_subsets_100: a hermax (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install hermax`):
#   python session2_subsets_100.py session2_subsets_100.json

from hermax.model import Model


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets S and T
    of A whose elements have the same sum. S and T need not cover all of A."""
    A = instance["A"]  # A[i]: the i-th integer of the set
    n = len(A)  # n: how many integers A holds

    m = Model()

    # in_S[i] is true when the element A[i] belongs to the subset S
    in_S = m.bool_vector("S", n)
    # in_T[i] is true when the element A[i] belongs to the subset T
    in_T = m.bool_vector("T", n)

    # S and T are disjoint: no element is in both.
    for i in range(n):
        m &= (~in_S[i] | ~in_T[i])

    # S is non-empty.
    m &= in_S.at_least_one()
    # T is non-empty.
    m &= in_T.at_least_one()

    # The elements of S and the elements of T have the same sum.
    m &= (sum(A[i] * in_S[i] for i in range(n)) == sum(A[i] * in_T[i] for i in range(n)))

    return m, {"in_S": in_S, "in_T": in_T}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
