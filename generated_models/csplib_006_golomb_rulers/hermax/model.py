# csplib_006_golomb_rulers: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from hermax.model import Model


def create_model(instance):
    """Golomb ruler: place `size` marks at whole-number positions 0 = a_1 < a_2 < ... < a_size
    so that the distances between every pair of marks are all different, and make the
    length of the ruler (the position of the last mark) as small as possible."""
    size = instance["size"]  # size: the number of marks on the ruler

    # Upper bound on the length of the ruler. The optimal lengths for these sizes are well
    # below size * size (for example 55 for 10 marks), so this bound does not cut off the optimum.
    upper = size * size

    m = Model()

    # marks[k] is the position of mark k+1. Mark k is preceded by k gaps, which are distinct
    # positive whole numbers, so it is at least 1 + 2 + ... + k = k(k+1)/2. The r = size-1-k
    # gaps after it likewise need at least r(r+1)/2 more units to fit before the upper bound.
    marks = []
    bounds = []
    for k in range(size):
        lowest = k * (k + 1) // 2
        room_after = size - 1 - k
        # The first mark is at position 0, so its domain is just 0.
        highest = 0 if k == 0 else upper - room_after * (room_after + 1) // 2
        bounds.append((lowest, highest))
        marks.append(m.int(f"mark_{k}", lowest, highest))

    # The marks are in increasing order along the ruler.
    for k in range(size - 1):
        m &= (marks[k] < marks[k + 1])

    # occupied[p] is true exactly when some mark sits at position p.
    # Encoding note: the Golomb condition below is posted over these Booleans and pair
    # indicators (pure clauses) rather than as all_different over the distances. Measured on the
    # 10-mark instance: 23 s to prove the optimum, against 151 s for all_different over the
    # size*(size-1)/2 distance IntVars.
    occupied = m.bool_vector("occupied", upper + 1)
    for p in range(upper + 1):
        # Only marks whose domain contains p can sit there.
        here = [k for k in range(size) if bounds[k][0] <= p <= bounds[k][1]]
        # a mark at p makes position p occupied
        for k in here:
            m &= (~(marks[k] == p) | occupied[p])
        # an occupied position has some mark on it
        clause = ~occupied[p]
        for k in here:
            clause = clause | (marks[k] == p)
        m &= clause

    # Golomb condition: for each distance d, at most one pair of positions p, p+d is occupied,
    # so the size*(size-1)/2 distances between pairs of marks are all different.
    for d in range(1, upper + 1):
        pair = m.bool_vector(f"pair_{d}", upper - d + 1)
        for p in range(upper - d + 1):
            m &= (~occupied[p] | ~occupied[p + d] | pair[p])
        m &= pair.at_most_one()

    # Minimise the length of the ruler, which is the position of the last mark.
    length = marks[size - 1]
    m.obj += length

    return m, {"length": length, "marks": marks}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
