# de_bruijn_sequence: a PuLP (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

import pulp


def create_model(instance):
    """A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
    sequence of length base**n in which every string of n symbols occurs exactly
    once as a substring. Find such a sequence."""
    base = instance["base"]  # the number of symbols in the alphabet
    n = instance["n"]        # the length of the strings that must each occur once
    n_strings = base**n      # the number of such strings, which is also the length of the sequence

    problem = pulp.LpProblem("de_bruijn", pulp.LpMinimize)  # the puzzle asks for any such sequence

    def digit(v, j):
        """The symbol in place j (0 is the first) of the string with number v. A string
        is read as a number in base `base`, with its first symbol the most significant."""
        return (v // base ** (n - 1 - j)) % base

    # symbol[k][a] is 1 when the sequence has symbol a at position k
    symbol = pulp.LpVariable.dicts("symbol", (range(n_strings), range(base)), cat="Binary")
    # Each position holds exactly one symbol.
    for k in range(n_strings):
        problem += pulp.lpSum(symbol[k][a] for a in range(base)) == 1
    # de_bruijn[k] is the symbol at position k.
    de_bruijn = [pulp.lpSum(a * symbol[k][a] for a in range(base)) for k in range(n_strings)]

    # string_at[i][v] is 1 when the string of n symbols starting at position i is the string with number v.
    string_at = pulp.LpVariable.dicts("string_at", (range(n_strings), range(n_strings)), cat="Binary")
    # Each position starts exactly one string.
    for i in range(n_strings):
        problem += pulp.lpSum(string_at[i][v] for v in range(n_strings)) == 1
    # Each string occurs at exactly one position.
    for v in range(n_strings):
        problem += pulp.lpSum(string_at[i][v] for i in range(n_strings)) == 1

    # The string starting at position i has symbol a in place j exactly when the sequence
    # has symbol a at position i + j, wrapping around the end.
    for i in range(n_strings):
        for j in range(n):
            for a in range(base):
                problem += pulp.lpSum(
                    string_at[i][v] for v in range(n_strings) if digit(v, j) == a
                ) == symbol[(i + j) % n_strings][a]

    return problem, {"de_bruijn": de_bruijn}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
