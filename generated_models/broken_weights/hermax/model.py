# broken_weights: a hermax (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install hermax`):
#   python broken_weights.py broken_weights.json
from hermax.model import Model


def create_model(instance):
    """A measuring weight of `total` pounds broke into `n` pieces, each a whole number of
    pounds. Find the weights of the pieces so that they add up to the original weight and,
    on a balance (a piece may go on the object's pan, on the other pan, or be left off),
    every whole weight from 1 up to `total` can be weighed."""
    total = instance["m"]  # total: the weight of the measuring weight before it broke, in pounds
    n = instance["n"]      # n: the number of pieces it broke into

    m = Model()

    # weights[j] is the weight of piece j, a whole number of pounds from 1 to total
    weights = m.int_vector("weights", n, 1, total)

    # The pieces add up to the original weight.
    m &= (sum(weights[j] for j in range(n)) == total)

    # Every target t from 1 to total must be weighable. For a target t, each piece j
    # contributes to the balance: +weights[j] when it sits on the other pan (it adds to
    # the object's weight), -weights[j] when it sits on the object's pan, and 0 when it
    # is left off. The contributions must add up to exactly t.
    for t in range(1, total + 1):
        # contribution[j] is what piece j adds to the balance for target t
        contribution = [m.int(f"contribution_{t}_{j}", -total, total) for j in range(n)]
        for j in range(n):
            # pan[j][0]: piece j is on the other pan; pan[j][1]: on the object's pan;
            # pan[j][2]: piece j is left off. Exactly one of the three holds.
            pan = m.bool_vector(f"pan_{t}_{j}", 3)
            m &= pan.exactly_one()
            # the contribution follows the pan the piece is on
            m &= (contribution[j] == weights[j]).only_if(pan[0])
            m &= (contribution[j] + weights[j] == 0).only_if(pan[1])
            m &= (contribution[j] == 0).only_if(pan[2])
        # the pieces balance the object of weight t
        m &= (sum(contribution[j] for j in range(n)) == t)

    return m, {"weights": weights}


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
