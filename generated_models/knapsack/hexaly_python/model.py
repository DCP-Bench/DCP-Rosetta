"""Knapsack: choose items within the weight capacity so that their total value is as large as possible."""
import hexaly.optimizer as hx


def build(instance):
    # values[i], weights[i] = value and weight of item i; capacity = largest total weight the backpack can carry
    values, weights, capacity = instance["values"], instance["weights"], instance["capacity"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] = 1 if item i goes into the backpack
    x = [model.bool() for _ in values]

    # The total weight of the chosen items must not exceed the capacity of the backpack
    model.constraint(model.sum(w * xi for w, xi in zip(weights, x)) <= capacity)
    # Maximise the total value of the chosen items
    model.maximize(model.sum(v * xi for v, xi in zip(values, x)))
    return optimizer, {"x": x}
