from hermax.model import Model


def build(instance):
    caps = instance["capacities"]          # bucket capacities
    init = instance["initial_state"]
    goal = instance["goal_state"]
    T = instance["MAX_STEPS"]              # number of states in the sequence, including the initial one
    PAD = instance["PADDING_VALUE"]
    B = len(caps)

    # Sequence state t is live (a real state) or padding (all buckets PAD).
    # A transfer pours from bucket a into bucket b until a is empty or b is full.
    # Live states are downward closed: once padding starts, it stays padding.
    m = Model()
    lo = min(PAD, 0)
    hi = max(max(caps), PAD)
    st = m.int_matrix("sequence", T, B, lo, hi)
    live = [m.bool() for _ in range(T)]

    m &= live[0]
    for k in range(B):
        m &= (st[0][k] == init[k])

    for t in range(T):
        for k in range(B):
            pad = (st[t][k] == PAD)
            m &= (live[t] | pad)                   # padding when not live
            m &= (~live[t] | ~pad)                 # not padding when live
            m &= (~live[t] | (st[t][k] >= 0))
            m &= (st[t][k] <= caps[k])

    # Transitions between state t and t+1: one pour when t+1 is live, none otherwise.
    for t in range(T - 1):
        m &= (~live[t + 1] | live[t])
        s, ns = st[t], st[t + 1]
        moves = []
        for a in range(B):
            for b in range(B):
                if a == b:
                    continue
                mv = m.bool()
                moves.append(mv)
                m &= (~mv | live[t + 1])
                # Water conserved between a and b, the other buckets unchanged.
                for c in range(B):
                    if c not in (a, b):
                        m &= (ns[c] == s[c]).only_if(mv)
                m &= (ns[a] + ns[b] == s[a] + s[b]).only_if(mv)
                m &= (ns[b] >= s[b]).only_if(mv)
                # Pour until a is empty or b is full.
                m &= (~mv | (ns[a] == 0) | (ns[b] == caps[b]))
        m &= (sum(moves) == 1).only_if(live[t + 1])

    # The goal is one of the live states.
    goal_flags = []
    for t in range(T):
        g = m.bool()
        goal_flags.append(g)
        m &= (~g | live[t])
        for k in range(B):
            m &= (~g | (st[t][k] == goal[k]))
    m &= (sum(goal_flags) >= 1)

    # Cost: one transfer for each live state after the initial one.
    cost = sum(live[t] for t in range(1, T))
    m.obj += cost

    return m, {"cost": cost, "sequence": st}
