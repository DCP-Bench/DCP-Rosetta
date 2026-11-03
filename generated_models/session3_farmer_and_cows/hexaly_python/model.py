"""Farmer and cows: give each son the stated number of cows so that every son gets the same total milk (cow i gives i).

The cows are numbered 1 to num_cows and cow i gives i units of milk. The farmer distributes
them to his sons following a given distribution of how many cows each son gets.
"""
import hexaly.optimizer as hx


def build(instance):
    # num_cows: number of cows, numbered 1 to num_cows; num_sons: number of sons
    # cows_per_son[s]: how many cows son s must receive
    cows, sons, per_son = instance["num_cows"], instance["num_sons"], instance["cows_per_son"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # gets[c][s] = 1 if cow c + 1 goes to son s
    gets = [[model.bool() for _ in range(sons)] for _ in range(cows)]

    # Every cow goes to exactly one son
    for c in range(cows):
        model.constraint(model.sum(gets[c]) == 1)
    # Son s gets exactly cows_per_son[s] cows, as the given distribution says
    for s in range(sons):
        model.constraint(model.sum(gets[c][s] for c in range(cows)) == per_son[s])
    # milk[s] is the total milk of son s: cow c + 1 gives c + 1 units of milk
    milk = [model.sum((c + 1) * gets[c][s] for c in range(cows)) for s in range(sons)]
    # The total quantity of milk is the same for each son: every son matches son 0
    for s in range(1, sons):
        model.constraint(milk[s] == milk[0])

    # cow_assignments[c] is the son (0-based) of cow c + 1, the only 1 in gets[c]
    cow_assignments = [model.sum(s * gets[c][s] for s in range(sons)) for c in range(cows)]
    return optimizer, {"cow_assignments": cow_assignments}
