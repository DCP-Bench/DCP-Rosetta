"""Rehearsal: order the pieces so that the total time players are present but not playing is minimal."""
import hexaly.optimizer as hx


def build(instance):
    n, duration, plays = instance["num_pieces"], instance["duration"], instance["rehearsal"]  # plays[p][q]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # rehearsal_order is a permutation of the pieces: a full list decision
    order = model.list(n)
    model.constraint(model.count(order) == n)
    slot = [model.index(order, q) for q in range(n)]  # the slot in which piece q is rehearsed

    waiting = []
    for p, row in enumerate(plays):
        mine = [q for q in range(n) if row[q]]
        if not mine:
            continue
        # A player arrives just before their first piece and leaves just after their last
        arrive = model.min(slot[q] for q in mine)
        leave = model.max(slot[q] for q in mine)
        # They wait through every piece they do not play that is rehearsed in between
        for q in range(n):
            if not row[q]:
                waiting.append(duration[q] * model.and_(arrive < slot[q], slot[q] < leave))

    # Minimise the total waiting time
    model.minimize(model.sum(waiting))
    return optimizer, {"rehearsal_order": order}
