from hermax.model import Model


def build(instance):
    numbers = instance["numbers"]

    m = Model()
    # Three integers, each between 1 and 10 inclusive.
    x = m.int_vector("x", 3, 1, 10)

    # Each non-empty subset of the three integers, as the indices it sums.
    subsets = [[j for j in range(3) if mask >> j & 1] for mask in range(1, 8)]

    # Every given number must be the sum of some subset of x.
    for n in numbers:
        options = []
        for subset in subsets:
            hit = m.bool()
            m &= (sum(x[j] for j in subset) == n).iff(hit)
            options.append(hit)
        m &= (options[0] | options[1] | options[2] | options[3]
              | options[4] | options[5] | options[6])

    return m, {"x": x}
