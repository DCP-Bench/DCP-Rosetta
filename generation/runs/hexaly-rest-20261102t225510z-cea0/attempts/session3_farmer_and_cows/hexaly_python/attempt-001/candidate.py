"""Farmer and cows: give each son the stated number of cows so that every son gets the same total milk (cow i gives i)."""
import hexaly.optimizer as hx


def build(instance):
    cows, sons, per_son = instance["num_cows"], instance["num_sons"], instance["cows_per_son"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # gets[c][s] = 1 if cow c + 1 goes to son s
    gets = [[model.bool() for _ in range(sons)] for _ in range(cows)]

    # Every cow goes to exactly one son
    for c in range(cows):
        model.constraint(model.sum(gets[c]) == 1)
    # Son s gets exactly cows_per_son[s] cows
    for s in range(sons):
        model.constraint(model.sum(gets[c][s] for c in range(cows)) == per_son[s])
    # Cow c + 1 gives c + 1 milk, and every son gets the same quantity in total
    milk = [model.sum((c + 1) * gets[c][s] for c in range(cows)) for s in range(sons)]
    for s in range(1, sons):
        model.constraint(milk[s] == milk[0])

    # The son (0-based) of each cow
    cow_assignments = [model.sum(s * gets[c][s] for s in range(sons)) for c in range(cows)]
    return optimizer, {"cow_assignments": cow_assignments}
