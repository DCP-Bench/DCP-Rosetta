# csplib_024_langford: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_024_langford.py csplib_024_langford.json

from hermax.model import Model


def create_model(instance):
    """Langford's problem: arrange two copies of each number 1..k in one sequence of
    length 2k so that the two copies of number i have exactly i numbers between them,
    that is they sit i + 1 places apart. Report the sequence as sol."""
    k = instance["k"]  # k: the largest number; each of 1..k appears twice
    length = 2 * k     # the sequence has 2k places, numbered 0..2k-1

    m = Model()

    # sol[p] is the number standing at place p of the sequence
    sol = m.int_vector("sol", length, 1, k)

    # first[i-1] is the place of the first copy of number i; the copy must fit, so it
    # starts no later than place 2k - i - 2
    first = [m.int(f"first_{i}", 0, length - i - 2) for i in range(1, k + 1)]
    # second[i-1] is the place of the second copy of number i
    second = [m.int(f"second_{i}", i + 1, length - 1) for i in range(1, k + 1)]

    # The second copy of number i sits i + 1 places after its first copy.
    for i in range(1, k + 1):
        m &= (second[i - 1] == first[i - 1] + i + 1)

    # Every place of the sequence holds exactly one copy: the 2k copy positions are all different.
    m &= m.vector(first + second).all_different()

    # Both places of each number's copies show that number in sol.
    for i in range(1, k + 1):
        m &= (sol[first[i - 1]] == i)
        m &= (sol[second[i - 1]] == i)

    return m, {"sol": sol}


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
