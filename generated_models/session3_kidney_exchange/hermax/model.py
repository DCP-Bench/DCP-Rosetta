# session3_kidney_exchange: a hermax (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install hermax`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from hermax.model import Model


def create_model(instance):
    """Kidney exchange: n people on a waiting list, each of whom can donate a kidney to
    some of the others. Choose the transplants so that anyone who gives a kidney also
    receives one and nobody gives or receives more than one kidney, with as many
    transplants as possible."""
    n = instance["num_people"]  # number of people on the waiting list
    # compatible[i] lists the people (numbered from 1) that person i can donate a kidney to
    compatible = instance["compatible"]

    # donates_to[i] is the set of people (numbered from 0 here) that person i can donate to
    donates_to = [set(j - 1 for j in compatible[i]) for i in range(n)]

    m = Model()

    # transplants[i][j] is true when person i donates a kidney to person j
    transplants = m.bool_matrix("transplants", n, n)

    # Only a compatible donor and recipient can be matched: every other pair is forced to no transplant.
    for i in range(n):
        for j in range(n):
            if j not in donates_to[i]:
                m &= ~transplants[i][j]

    for i in range(n):
        # Each person gives at most one kidney.
        m &= transplants.row(i).at_most_one()
        # Each person receives at most one kidney.
        m &= transplants.col(i).at_most_one()
        # Anyone who gives a kidney must receive one: the kidneys person i gives (0 or 1)
        # are at most the kidneys person i receives (0 or 1).
        m &= (sum(transplants[i][j] for j in range(n)) <= sum(transplants[k][i] for k in range(n)))

    # Maximise the number of transplants: minimise the negated count of transplants made.
    num_transplants = sum(transplants[i][j] for i in range(n) for j in donates_to[i])
    m.obj += -num_transplants

    # The objective in the problem's terms: the number of transplants (people who receive a kidney),
    # whose negation the solver minimises; incompatible pairs are forced false.
    return m, {"transplants": transplants}, num_transplants


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
