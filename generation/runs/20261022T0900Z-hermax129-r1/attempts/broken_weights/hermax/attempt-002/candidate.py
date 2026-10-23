from hermax.model import Model


def build(instance):
    total = instance["m"]   # total weight of the broken pieces (pounds)
    n = instance["n"]       # number of pieces

    m = Model()

    # Piece weights: whole pounds between 1 and the total, all different.
    weights = m.int_vector("weight", n, 1, total)
    m &= weights.all_different()
    # Pieces together make up the whole weight.
    m &= (sum(weights[i] for i in range(n)) == total)
    # Canonical order, so each multiset of pieces appears once.
    m &= weights.increasing()

    # For every target k in 1..total, pieces are placed on the two pans:
    # pan_pos[k][i] = weight_i if piece i is on the object's side, else 0;
    # pan_neg[k][i] = weight_i if piece i is on the weight side, else 0.
    # Then sum(pan_pos) - sum(pan_neg) must equal k.
    for k in range(1, total + 1):
        pos_terms = []
        neg_terms = []
        for i in range(n):
            on_pos = m.bool()
            on_neg = m.bool()
            pos = m.int(f"pos_{k}_{i}", 0, total)
            neg = m.int(f"neg_{k}_{i}", 0, total)
            # Value equals the piece weight when selected, and 0 otherwise.
            m &= (pos == weights[i]).only_if(on_pos)
            m &= (pos == 0).only_if(~on_pos)
            m &= (neg == weights[i]).only_if(on_neg)
            m &= (neg == 0).only_if(~on_neg)
            pos_terms.append(pos)
            neg_terms.append(neg)
        m &= (sum(pos_terms) - sum(neg_terms) == k)

    return m, {"weights": weights}
