# csplib_044_steiner: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_044_steiner.py csplib_044_steiner.json

from hermax.model import Model


def create_model(instance):
    """Ternary Steiner system of order n: choose n*(n-1)/6 triples of distinct elements
    from 1..n so that any two triples have at most one common element. Since the triples
    cover 3 pairs each, every pair of elements then lies in exactly one triple."""
    n = instance["n"]  # n: the order of the system, the elements are 1..n (n mod 6 is 1 or 3)

    # The number of triples the system needs: n*(n-1)/6
    num_triples = n * (n - 1) // 6

    m = Model()

    # sets[i][j] is true when element j (column j stands for element j+1) is in triple i
    sets = m.bool_matrix("sets", num_triples, n)

    # Each triple has exactly three elements.
    for i in range(num_triples):
        m &= (sum(sets[i][k] for k in range(n)) == 3)

    # Any two elements lie together in exactly one triple. This is the same as saying that
    # two triples share at most one element, plus the count: the triples cover
    # 3 * n(n-1)/6 = n(n-1)/2 pairs, so no pair can be covered twice nor left uncovered.
    for a in range(n):
        for b in range(a + 1, n):
            # together[i] is true exactly when triple i contains both element a and element b
            together = m.bool_vector(f"together_{a}_{b}", num_triples)
            for i in range(num_triples):
                m &= (sets[i][a] + sets[i][b] == 2).iff(together[i])
            # Exactly one triple contains the pair {a, b}.
            m &= (sum(together[i] for i in range(num_triples)) == 1)

    # Redundant counting constraint: each element is paired with the other n-1 elements,
    # and each triple that holds an element pairs it with two others, so it lies in (n-1)/2 triples.
    for k in range(n):
        m &= (sum(sets[i][k] for i in range(num_triples)) == (n - 1) // 2)

    # A Steiner system has no objective: any system meeting the constraints is an answer.
    return m, {"sets": sets}


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
