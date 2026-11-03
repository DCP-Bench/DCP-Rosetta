# csplib_019_magic_squares_and_sequences: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

from hermax.model import Model


def create_model(instance):
    """Magic sequence: find x[0], ..., x[n-1], each between 0 and n-1, such that for every
    i the number i occurs exactly x[i] times in the sequence. Satisfaction problem."""
    n = instance["n"]  # n: the length of the sequence

    m = Model()

    # x[i] is how many times the number i occurs in the sequence; the values lie in 0..n-1
    x = m.int_vector("x", n, 0, n - 1)

    # For every i, the number i occurs exactly x[i] times: the count of positions j
    # whose value x[j] equals i must be x[i].
    for i in range(n):
        m &= (sum((x[j] == i) for j in range(n)) == x[i])

    return m, {"x": x}


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
