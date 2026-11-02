"""Kidney exchange: donations between compatible people so that the most people receive a kidney,
everyone who gives also receives, and nobody receives more than one."""
import hexaly.optimizer as hx


def build(instance):
    n, compatible = instance["num_people"], instance["compatible"]  # compatible[i]: who i can donate to, 1-based
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # transplants[i][j] = 1 if person i donates to person j; only to a compatible person
    transplants = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in compatible[i]:
            transplants[i][j - 1] = model.bool()
    gives = [model.sum(transplants[i]) for i in range(n)]
    receives = [model.sum(transplants[i][j] for i in range(n)) for j in range(n)]

    for p in range(n):
        # A person has one kidney to give, and receives at most one
        model.constraint(gives[p] <= 1)
        model.constraint(receives[p] <= 1)
        # Anyone who gives a kidney must receive one
        model.constraint(gives[p] <= receives[p])

    # Maximise the number of people who receive a kidney
    model.maximize(model.sum(receives))
    return optimizer, {"transplants": transplants}
