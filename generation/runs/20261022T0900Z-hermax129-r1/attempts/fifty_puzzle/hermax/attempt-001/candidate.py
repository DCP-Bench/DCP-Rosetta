from hermax.model import Model


def build(instance):
    target_sum = instance["target_sum"]
    values = instance["values"]

    m = Model()
    # Boolean variables for each dummy: True if knocked over, False otherwise
    dummies = m.bool_vector("dummies", len(values))

    # Constraint: sum of selected dummies must equal target_sum
    m &= (sum(values[i] * dummies[i] for i in range(len(values))) == target_sum)

    return m, {"dummies": dummies}
