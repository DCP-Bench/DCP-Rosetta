# csplib_015_schurs_lemma: a CPMpy model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

import cpmpy as cp


def create_model(instance):
    """Put n balls labelled 1, ..., n into c boxes so that for any triple of balls
    (x, y, z) with x + y = z, not all three are in the same box."""
    n = instance["n"]  # the number of balls, labelled 1..n
    c = instance["c"]  # the number of boxes, labelled 1..c

    # balls[i] is the box that ball i+1 is put in
    balls = cp.intvar(1, c, shape=n, name="balls")

    model = cp.Model()
    # For every x + y = z, the balls x, y and z are not all in the same box.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            model.add(~((balls[x - 1] == balls[y - 1]) & (balls[y - 1] == balls[z - 1])))

    return model, {"balls": balls}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
