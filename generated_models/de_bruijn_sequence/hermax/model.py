# de_bruijn_sequence: a hermax (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install hermax`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

from hermax.model import Model


def create_model(instance):
    """A de Bruijn sequence B(base, n): a cyclic sequence of `base` symbols, of length
    base**n, in which every string of n symbols occurs exactly once as a run of
    consecutive symbols (reading on past the end wraps around to the start)."""
    base = instance["base"]  # the size of the alphabet: the symbols are 0..base-1
    n = instance["n"]        # the order: the length of the strings that must all appear
    length = base ** n       # the sequence length, which is also the number of strings

    m = Model()

    # symbol[p] is the symbol at position p of the cyclic sequence
    symbol = m.int_vector("symbol", length, 0, base - 1)

    # window[i] is the n symbols starting at position i (wrapping around), read as a
    # number in base `base`; two windows are the same string exactly when their numbers match
    window = m.int_vector("window", length, 0, base ** n - 1)
    for i in range(length):
        m &= (window[i] == sum(base ** (n - 1 - j) * symbol[(i + j) % length]
                               for j in range(n)))

    # Every string of n symbols occurs exactly once: all the windows are different.
    m &= window.all_different()

    # No objective: any sequence meeting the constraints is a de Bruijn sequence.
    return m, {"de_bruijn": symbol}


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
