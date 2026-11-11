# csplib_015_schurs_lemma: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from pycsp3 import *


def create_model(instance):
    """Put n balls labelled 1, ..., n into c boxes (the problem has c = 3) so that for any triple of balls
    (x, y, z) with x + y = z, where x and y may be equal, not all three are in the same box."""
    n_balls = instance["n"]   # the number of balls
    n_boxes = instance["c"]   # the number of boxes

    # balls[i - 1] is the box, numbered 1 to n_boxes, of the ball labelled i (the balls are labelled from 1).
    balls = VarArray(size=n_balls, dom=range(1, n_boxes + 1))

    satisfy(
        # The balls x, y and x + y (x may equal y) are not all in one box. NotAllEqual is not used because
        # for x == y its scope repeats a variable, which ACE fails on.
        Or(balls[x - 1] != balls[y - 1], balls[y - 1] != balls[x + y - 1])
        for x in range(1, n_balls + 1)
        for y in range(x, n_balls - x + 1)
    )

    return {"balls": balls}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
