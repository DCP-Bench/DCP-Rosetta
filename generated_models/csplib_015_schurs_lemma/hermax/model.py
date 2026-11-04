# csplib_015_schurs_lemma: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from hermax.model import Model


def create_model(instance):
    """Schur's lemma: put the balls 1..n into c boxes so that no triple of balls
    (x, y, z) with x + y = z lies entirely in one box. Satisfaction problem."""
    n = instance["n"]  # the number of balls, labelled 1..n
    c = instance["c"]  # the number of boxes, numbered 1..c

    m = Model()

    # balls[i] is the box (1..c) of ball i + 1
    balls = m.int_vector("balls", n, 1, c)

    # Every triple (x, y, z) with x + y = z, 1 <= x <= y and z <= n, is not all in one box:
    # for each box j, at most two of the three balls x, y, z are in box j.
    for x in range(1, n + 1):
        for y in range(x, n + 1):
            z = x + y
            if z > n:
                continue
            for box in range(1, c + 1):
                # at most two of the balls x, y, z are in this box
                m &= (sum(balls[k - 1] == box for k in (x, y, z)) <= 2)

    return m, {"balls": balls}


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
