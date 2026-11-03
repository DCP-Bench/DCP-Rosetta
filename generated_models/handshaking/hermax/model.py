# handshaking: a hermax (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install hermax`):
#   python handshaking.py handshaking.json

from hermax.model import Model


def create_model(instance):
    """Hilary and Jocelyn, a married couple, invite some other couples to dinner. Everybody
    shakes hands with the others, except nobody shakes hands with themselves or with their
    own spouse. Afterwards Jocelyn asks how many hands each person shook, and all the answers
    are different (except Hilary's, which is not compared; leaving out Jocelyn's instead gives
    the same answer). Find how many hands Hilary shook."""
    # num_couples: how many couples are invited, not counting Hilary and Jocelyn
    num_couples = instance["num_couples"]
    # People in all: person 0 is Hilary, person 1 is Jocelyn, and the couples are (2, 3), (4, 5), ...
    n = 2 + 2 * num_couples

    m = Model()

    # hands[i] is how many hands person i shook; at most n - 2, since a person can shake
    # hands with everyone except themselves and their spouse
    hands = m.int_vector("hands", n, 0, n - 2)

    # shook[(i, j)] is true when persons i < j shook hands. A handshake is mutual, so one
    # Boolean per pair covers both directions. Spouses (i and i ^ 1) never shake hands,
    # so they get no variable.
    shook = {(i, j): m.bool(f"shook_{i}_{j}")
             for i in range(n) for j in range(i + 1, n) if j != (i ^ 1)}

    def partners(i):
        """The handshake variables that person i could take part in."""
        return [shook[(min(i, j), max(i, j))] for j in range(n) if j != i and j != (i ^ 1)]

    # hands[i] is the number of handshakes person i takes part in
    for i in range(n):
        m &= (sum(partners(i)) == hands[i])

    # Everyone except Hilary has a different count. Hilary's count is left out as in the
    # reference; leaving out Jocelyn's instead gives the same answer, since both spouses of
    # the hosting couple shake num_couples hands.
    m &= m.vector([hands[i] for i in range(1, n)]).all_different()

    # Symmetry breaking (does not change Hilary's count): spouses are interchangeable, and so
    # are whole couples. Within each couple the first spouse has the smaller count (their counts
    # differ), and the couples are listed by the count of their first spouse. Every solution can
    # be rearranged this way with the same hands[0], so only the search gets shorter.
    for c in range(1, num_couples + 1):
        m &= (hands[2 * c] < hands[2 * c + 1])
        if c < num_couples:
            m &= (hands[2 * c] < hands[2 * c + 2])

    # Hilary's count is the answer
    return m, {"hil": hands[0]}


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
