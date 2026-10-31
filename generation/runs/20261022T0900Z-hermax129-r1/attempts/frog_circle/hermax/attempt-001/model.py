from hermax.model import Model


def build(instance):
    """
    Frog circle: arrange cards 1 to n such that jumping by card value visits all positions.
    x[p] = card value at position p. Starting from position 0, jump (x[p] mod n) positions.
    The frog must visit all n positions exactly once.
    """
    n = instance["n"]

    m = Model()

    # x[p] is the card value at position p - must be a permutation of 1 to n
    x = m.int_vector("x", n, 1, n)
    m &= x.all_different()

    # For each position p, pre-compute where it jumps to
    # next_jump[p] = (p + x[p]) % n
    next_jump = []
    for p in range(n):
        sum_p = p + x[p]
        next_p = m.int(f"next_jump_{p}", 0, n-1)

        # Encode modulo: if sum_p < n, next_p = sum_p; else next_p = sum_p - n
        wrap = m.bool(f"wrap_{p}")
        m &= (wrap | (sum_p <= n - 1))
        m &= (~wrap | (sum_p >= n))

        m &= (next_p == sum_p - n * wrap)
        next_jump.append(next_p)

    # Now, enforce that starting from position 0 and following next_jump,
    # we visit all positions exactly once and return to 0 after n jumps.
    # This means next_jump forms a single cycle of length n starting from 0.

    # visited[i] is the position visited at step i
    visited = m.int_vector("visited", n, 0, n-1)
    m &= (visited[0] == 0)  # Start at position 0
    m &= visited.all_different()  # All distinct positions

    # For each step i, visited[i+1] = next_jump[visited[i]]
    # This requires indexing next_jump with visited[i]
    # We encode this by iterating over all possible position values
    for i in range(n-1):
        # For each possible position p that could be at visited[i],
        # constrain visited[i+1] to be next_jump[p]

        # Create auxiliary variable for next_jump[visited[i]]
        jump_target = m.int(f"jump_target_{i}", 0, n-1)

        # For each position p: if visited[i] == p, then jump_target == next_jump[p]
        for p in range(n):
            # (~visited[i] == p) | (jump_target == next_jump[p])
            # Use: (visited[i] != p) | (jump_target == next_jump[p])
            m &= ((visited[i] != p) | (jump_target == next_jump[p]))

        # visited[i+1] must equal jump_target
        m &= (visited[i+1] == jump_target)

    # Enforce cycle closes: after last position, we should return to 0
    jump_target_last = m.int("jump_target_last", 0, n-1)
    for p in range(n):
        m &= ((visited[n-1] != p) | (jump_target_last == next_jump[p]))
    m &= (jump_target_last == 0)  # Must return to position 0

    return m, {"x": x}
