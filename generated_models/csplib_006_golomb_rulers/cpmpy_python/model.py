# csplib_006_golomb_rulers: a CPMpy model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

import cpmpy as cp


def create_model(instance):
    """Place marks on a ruler, the first at position 0, so that the differences between
    all pairs of marks are distinct. Find the shortest such Golomb ruler."""
    size = instance["size"]  # the number of marks on the ruler

    # marks[i] is the position of mark i. size * size bounds the positions: the
    # shortest ruler with this many marks is known to be far shorter.
    marks = cp.intvar(0, size * size, shape=size, name="marks")
    # length is the length of the ruler: the position of its last mark
    length = marks[-1]

    model = cp.Model()
    # The first mark is at position 0.
    model.add(marks[0] == 0)
    # The marks are placed in strictly increasing order of position.
    model.add(marks[:-1] < marks[1:])
    # Golomb condition: the differences between all pairs of marks are distinct.
    diffs = [marks[j] - marks[i] for i in range(size - 1) for j in range(i + 1, size)]
    model.add(cp.AllDifferent(diffs))

    # Find the shortest ruler.
    model.minimize(length)

    return model, {"marks": marks, "length": length}


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
