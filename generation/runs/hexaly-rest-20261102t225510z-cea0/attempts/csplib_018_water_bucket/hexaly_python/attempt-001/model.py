"""Water bucket: pour water between buckets until the goal state is reached with the fewest transfers."""
import hexaly.optimizer as hx


def build(instance):
    cap, initial, goal = instance["capacities"], instance["initial_state"], instance["goal_state"]
    steps, pad = instance["MAX_STEPS"], instance["PADDING_VALUE"]
    n = len(cap)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # real[t] = 1 while state t is still part of the sequence; the sequence starts at the initial state
    # and the goal ends it, after which only padding follows
    real = [1] + [model.bool() for _ in range(steps - 1)]
    state = [list(initial)] + [[model.int(0, cap[b]) for b in range(n)] for _ in range(steps - 1)]

    for t in range(steps - 1):
        model.constraint(real[t + 1] <= real[t])
        # pour[f, g] = 1 if the transfer into state t + 1 goes from bucket f to bucket g
        pour = {(f, g): model.bool() for f in range(n) for g in range(n) if f != g}
        model.constraint(model.sum(list(pour.values())) == real[t + 1])
        amount = model.int(0, max(cap))
        model.constraint(amount <= max(cap) * real[t + 1])
        for (f, g), p in pour.items():
            room = cap[g] - state[t][g]
            # A transfer moves water until bucket f is empty or bucket g is full, and is not empty
            model.constraint(model.or_(p == 0, model.and_(
                amount >= 1, amount <= state[t][f], amount <= room,
                model.or_(amount == state[t][f], amount == room))))
        # The next state: bucket b loses what it pours out and gains what is poured in
        for b in range(n):
            out = model.sum([pour[b, g] for g in range(n) if g != b]) * amount
            gain = model.sum([pour[f, b] for f in range(n) if f != b]) * amount
            model.constraint(state[t + 1][b] == state[t][b] - out + gain)
        # The sequence ends at the first goal state, so a goal state is never followed by a transfer
        model.constraint(model.or_(real[t + 1] == 0, model.or_(*[state[t][b] != goal[b] for b in range(n)])))

    # The last state of the sequence is the goal state
    for t in range(steps):
        conditions = ([real[t] == 1] if t else []) + ([real[t + 1] == 0] if t + 1 < steps else [])
        last = model.and_(*conditions) if len(conditions) > 1 else conditions[0]
        model.constraint(model.or_(model.not_(last), model.and_(*[state[t][b] == goal[b] for b in range(n)])))

    # Minimise the number of transfers, one for every state after the first
    cost = model.sum(real[1:])
    model.minimize(cost)

    # The states of the sequence, padded after the goal
    sequence = [[state[t][b] if t == 0 else model.iif(real[t], state[t][b], pad) for b in range(n)]
                for t in range(steps)]
    return optimizer, {"cost": cost, "sequence": sequence}
