from hermax.model import Model


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    m = Model()
    take = m.bool_vector("take", n)

    # The total weight of the items taken must not exceed the backpack capacity.
    m &= (sum(weights[j] * take[j] for j in range(n)) <= capacity)

    # Maximise the total value carried: pay for every item left behind.
    for j, value in enumerate(values):
        m.obj[value] += take[j]

    return m, {"x": take}
