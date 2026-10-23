from hermax.model import Model


def build(instance):
    graph = instance["graph"]
    # The problem fixes six countries.
    n = 6
    # Colours are integers 1..n.
    m = Model()

    # paint[i][k] is true when country i has colour k + 1.
    paint = m.bool_matrix("paint", n, n)
    # colors[i] is the colour of country i, from 1 to n.
    colors = m.int_vector("colors", n, 1, n)

    # Each country gets exactly one colour.
    for i in range(n):
        m &= paint.row(i).exactly_one()
        m &= (colors[i] == sum((k + 1) * paint[i][k] for k in range(n)))

    # Two neighbouring countries cannot have the same colour.
    for a, b in graph:
        a -= 1
        b -= 1
        for k in range(n):
            m &= (~paint[a][k] | ~paint[b][k])

    # used[k] is true when some country has colour k + 1.
    used = m.bool_vector("used", n)
    for i in range(n):
        for k in range(n):
            m &= (~paint[i][k] | used[k])

    # Colours are interchangeable, so use the lowest numbers first: colour k + 2 is used
    # only if colour k + 1 is used. Any colouring can be renumbered this way.
    for k in range(n - 1):
        m &= (used[k] | ~used[k + 1])

    # Minimise the number of colours used.
    m.obj += sum(used[k] for k in range(n))

    return m, {"colors": colors}
