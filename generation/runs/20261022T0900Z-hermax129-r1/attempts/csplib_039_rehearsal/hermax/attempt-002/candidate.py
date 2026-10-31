from hermax.model import Model


def build(instance):
    n = instance["num_pieces"]
    n_players = instance["num_players"]
    dur = instance["duration"]
    plays = instance["rehearsal"]          # plays[player][piece] in {0, 1}
    horizon = sum(dur)                     # all pieces back to back

    m = Model()
    # before[p][q]: piece p is rehearsed before piece q (off-diagonal only).
    before = m.bool_matrix("before", n, n)
    # st[p]: start time of piece p.
    st = m.int_vector("piece_start", n, 0, horizon)
    # rank[p]: position of piece p in the rehearsal order.
    rank = m.int_vector("rank", n, 0, n - 1)
    order = m.int_vector("order", n, 0, n - 1)

    # Every pair of pieces is ordered one way or the other, never both.
    for p in range(n):
        for q in range(p + 1, n):
            m &= before[p][q] | before[q][p]
            m &= (~before[p][q]) | (~before[q][p])

    # If p is before q, q starts after p has finished.
    for p in range(n):
        for q in range(n):
            if p != q:
                m &= before[p][q].implies(st[q] >= st[p] + dur[p])

    # The rank of a piece is the number of pieces rehearsed before it.
    for p in range(n):
        m &= (rank[p] == sum(before[q][p] for q in range(n) if q != p))

    # Output: the piece rehearsed in each slot.
    for p in range(n):
        for s in range(n):
            m &= (rank[p] == s).implies(order[s] == p)

    # Each player is present from the start of the first piece they play
    # until the end of the last one. The waiting time is that span minus the
    # time spent playing, and playing time is fixed, so minimise the span.
    start = m.int_vector("player_start", n_players, 0, horizon)
    end = m.int_vector("player_end", n_players, 0, horizon)
    for k in range(n_players):
        for p in range(n):
            if plays[k][p]:
                m &= (start[k] <= st[p])
                m &= (end[k] >= st[p] + dur[p])
    m.obj += sum(end[k] - start[k] for k in range(n_players))

    return m, {"rehearsal_order": order}
