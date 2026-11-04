# de_bruijn_sequence: a Python-MIP (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

import mip


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of length base**n in which every string of n symbols occurs exactly
    once as a substring. Find such a sequence."""
    base = instance["base"]        # the number of symbols in the alphabet
    n = instance["n"]              # the length of the strings that must all occur
    n_strings = base**n            # the number of strings, which is also the length of the sequence

    model = mip.Model()

    # seq[i] is the symbol at position i of the cyclic sequence
    seq = [model.add_var(f"s_{i}", lb=0, ub=base - 1, var_type=mip.INTEGER) for i in range(n_strings)]

    # word[i] is the string of n symbols starting at position i, read as a number in base
    word = [mip.xsum((base**j) * seq[(i + j) % n_strings] for j in range(n)) for i in range(n_strings)]

    # at_value[i][v] is 1 when the string starting at position i reads as the number v
    at_value = [[model.add_var(f"w_{i}_{v}", var_type=mip.BINARY) for v in range(n_strings)] for i in range(n_strings)]

    # The string starting at each position reads as exactly one number.
    for i in range(n_strings):
        model.add_constr(mip.xsum(at_value[i]) == 1)
        model.add_constr(mip.xsum(v * at_value[i][v] for v in range(n_strings)) == word[i])

    # No number is read by two strings, so every string occurs once.
    for v in range(n_strings):
        model.add_constr(mip.xsum(at_value[i][v] for i in range(n_strings)) <= 1)

    return model, {"de_bruijn": seq}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
