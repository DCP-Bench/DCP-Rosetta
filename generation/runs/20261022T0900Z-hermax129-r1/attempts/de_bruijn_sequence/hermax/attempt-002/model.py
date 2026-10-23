from hermax.model import Model


def build(instance):
    k = instance["base"]                  # alphabet size
    n = instance["n"]                     # order: length of each window
    length = k ** n                       # a de Bruijn sequence B(k, n) has k^n symbols

    m = Model()
    x = m.int_vector("x", length, 0, k - 1)
    # code[i]: the window of n symbols that starts at position i (cyclically),
    # read as a base-k number. Each window value is distinct, so every
    # length-n string appears exactly once.
    code = m.int_vector("code", length, 0, length - 1)
    for i in range(length):
        m &= (code[i] == sum(k ** (n - 1 - j) * x[(i + j) % length] for j in range(n)))
    m &= code.all_different()

    return m, {"de_bruijn": x}
