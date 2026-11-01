from hermax.model import Model


def build(instance):
    # Number of marks n comes from the instance.
    n = instance["n"]

    model = Model()

    # costas[i] is the column of the mark in row i, with values 1 .. n.
    costas = model.int_vector("costas", n, 1, n)

    # One mark per row and one per column: the values form a permutation.
    model &= costas.all_different()

    # Difference triangle: for each distance l = 1 .. n-1, the n-l differences
    # costas[i+l] - costas[i] must all be different. Each line of the triangle
    # is its own all-different constraint.
    for l in range(1, n):
        diffs = model.int_vector(f"diff_{l}", n - l, -(n - 1), n - 1)
        for i in range(n - l):
            model &= (diffs[i] == costas[i + l] - costas[i])
        model &= diffs.all_different()

    return model, {"costas": costas}
