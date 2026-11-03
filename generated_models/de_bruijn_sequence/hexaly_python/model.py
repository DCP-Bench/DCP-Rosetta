"""De Bruijn sequence: a cyclic sequence of length base^n over 0..base-1 containing every length-n string once."""
import hexaly.optimizer as hx


def build(instance):
    base, n = instance["base"], instance["n"]
    length = base ** n
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    de_bruijn = [model.int(0, base - 1) for _ in range(length)]

    # The length-n window starting at position i, read as a number in base `base`; the
    # sequence is cyclic, so windows wrap round the end
    window = [model.sum(de_bruijn[(i + k) % length] * base ** (n - 1 - k) for k in range(n))
              for i in range(length)]
    # Every length-n string occurs exactly once: the base^n windows are all different
    for i in range(length):
        for j in range(i + 1, length):
            model.constraint(window[i] != window[j])

    return optimizer, {"de_bruijn": de_bruijn}
