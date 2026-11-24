# de_bruijn_sequence: a PyCSP3 model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

from pycsp3 import *


def create_model(instance):
    """In combinatorial mathematics, a de Bruijn sequence of order n on a size-k alphabet A is a
    cyclic sequence in which every possible length-n string on A occurs exactly once as a
    substring. Such a sequence has length k^n."""
    base = instance["base"]      # k: the size of the alphabet, its symbols are 0 .. base - 1
    order = instance["n"]        # n: the length of the strings that must each occur once
    length = base ** order       # the sequence has base^order symbols, as the statement says

    # de_bruijn[i] is the symbol at position i of the cyclic sequence (0-based)
    de_bruijn = VarArray(size=length, dom=range(base))

    # Every string of `order` symbols occurs exactly once: the base-`base` number read from each
    # cyclic window of the sequence (first symbol most significant) is different for every starting
    # position. The sequence is cyclic, so a window running past the end wraps to the start.
    # There are base^order windows and base^order strings of length order, so all windows
    # being different means each string occurs exactly once.
    satisfy(
        AllDifferent(
            [
                Sum(base ** (order - 1 - offset) * de_bruijn[(i + offset) % length] for offset in range(order))
                for i in range(length)
            ]
        )
    )

    return {"de_bruijn": de_bruijn}


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
