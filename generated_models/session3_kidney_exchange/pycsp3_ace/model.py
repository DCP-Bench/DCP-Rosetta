# session3_kidney_exchange: a PyCSP3 model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from pycsp3 import *


def create_model(instance):
    """At a hospital, n people are on a waiting list for a kidney transplant. Compatibility
    is given as a directed graph: a person can donate to the people listed for them. Maximise
    the number of people who receive a new kidney: anyone who gives a kidney must receive one,
    and no person receives more than one kidney."""
    n_people = instance["num_people"]  # the number of people on the waiting list
    # compatible[i] is the list of people that person i + 1 can donate to. The listed people are
    # numbered from 1 (no entry is 0), so each is shifted by - 1 to a 0-based index.
    compatible = instance["compatible"]

    # donates_to[i] is the person (0-based) that person i donates a kidney to. donates_to[i] == i
    # means person i takes no part in an exchange.
    donates_to = VarArray(size=n_people, dom=lambda i: sorted({i, *(j - 1 for j in compatible[i])}))

    # transplants[i][j] is 1 when person i donates a kidney to person j (0-based), 0 otherwise
    transplants = VarArray(size=[n_people, n_people], dom={0, 1})

    satisfy(
        # No person receives more than one kidney, and a person who takes no part is not given a kidney.
        # Anyone who gives a kidney must receive one, so the donations form disjoint cycles: since each person donates
        # to one person (themselves if they take no part) and nobody receives two, donates_to is a permutation.
        AllDifferent(donates_to),
        # transplants[i][j] is 1 exactly when person i donates to person j.
        [(transplants[i][j] == 1) == (donates_to[i] == j) for i in range(n_people) for j in range(n_people) if j != i],
        # A person does not donate to themselves.
        [transplants[i][i] == 0 for i in range(n_people)],
    )

    # The number of people who receive a kidney: a person receives one exactly when they take part,
    # that is when they donate to someone else (donates_to[i] != i), since a participant's donor is
    # another person in the cycle.
    maximize(Sum(donates_to[i] != i for i in range(n_people)))

    return {"transplants": transplants}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("transplants", "=")
        for row in outputs["transplants"]:
            print(values(row))
    else:
        print("No solution:", status())
