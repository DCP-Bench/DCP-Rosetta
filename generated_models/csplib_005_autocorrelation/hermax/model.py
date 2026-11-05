# csplib_005_autocorrelation: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Choose a binary sequence of length n, each bit +1 or -1, with low periodic
    autocorrelation. For each shift k = 1..n-1 the periodic autocorrelation C_k is the
    sum over all i of S_i * S_((i+k) mod n). Minimise the energy, the sum of C_k squared."""
    n = instance["n"]  # length of the sequence (number of bits)

    m = Model()

    # sequence[i] is the i-th bit, -1 or +1 (0 is not a valid bit)
    sequence = m.int_vector("sequence", n, -1, 1)
    for i in range(n):
        m &= (sequence[i] != 0)

    # autocorrelation[k-1] is C_k, the periodic autocorrelation at shift k
    autocorrelation = []
    for k in range(1, n):
        # differs[i] is true when bit i and bit (i+k) mod n have different signs.
        # Their product is -1 then, and +1 otherwise.
        differs = m.bool_vector(f"differs_{k}", n)
        for i in range(n):
            m &= (sequence[i] != sequence[(i + k) % n]).iff(differs[i])

        # C_k = (positions with equal bits) - (positions with different bits)
        #     = n - 2 * (number of positions that differ)
        c = m.int(f"C_{k}", -n, n)  # the autocorrelation C_k, between -n and n
        m &= (c == n - 2 * sum(differs[i] for i in range(n)))
        autocorrelation.append(c)

    # Energy: the sum over k of C_k squared. Each square is written by cases on the value
    # of C_k, so the solver sees the cost of each possible C_k directly.
    energy = sum_expr(
        c.piecewise(base_value=n * n, steps={t: t * t for t in range(-n + 1, n + 1)})
        for c in autocorrelation)

    # Minimise the energy.
    m.obj += energy

    # The objective in the problem's terms: the energy E, the sum of the squared periodic
    # autocorrelations, the cost minimised above.
    return m, {"sequence": sequence}, energy


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
