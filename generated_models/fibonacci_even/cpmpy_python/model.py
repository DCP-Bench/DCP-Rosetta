# fibonacci_even: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install cpmpy`) with:
#   python fibonacci_even.py

import cpmpy as cp


def create_model(instance):
    """Each new term in the Fibonacci sequence is the sum of the previous two.
    Find the sum of the even-valued terms that do not exceed four million."""
    num_terms = 35      # enough terms to pass the cutoff
    cutoff = 4_000_000  # terms must not exceed four million

    # f[i] is the i-th Fibonacci term, with f[0] = 0 and f[1] = 1;
    # the upper bound is well above the cutoff and covers the first 35 terms
    f = cp.intvar(0, 10_000_000, shape=num_terms + 1, name="f")
    # counted[i] is true when term i is even and below the cutoff, so it is summed
    counted = cp.boolvar(shape=num_terms + 1, name="counted")
    # res is the sum of the counted terms
    res = cp.intvar(0, 100_000_000, name="res")

    model = cp.Model()

    # The sequence starts 0, 1, 1 and each later term is the sum of the previous two.
    model.add(f[0] == 0)
    model.add(f[1] == 1)
    model.add(f[2] == 1)
    model.add(f[3:] == f[2:-1] + f[1:-2])

    # A term is counted exactly when it is even and below the cutoff; term 0 is not counted.
    model.add(counted[0] == 0)
    model.add(counted[1:] == ((f[1:] % 2 == 0) & (f[1:] < cutoff)))

    # The result is the sum of the counted terms.
    model.add(res == cp.sum(counted[1:] * f[1:]))

    return model, {"res": res}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
