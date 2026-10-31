from hermax.model import Model


def build(instance):
    m = Model()

    # Boolean matrices: x[i][p] = True iff item i is at position p
    island_pos = m.bool_matrix("island_pos", 4, 4)
    export_pos = m.bool_matrix("export_pos", 4, 4)
    attraction_pos = m.bool_matrix("attraction_pos", 4, 4)

    # Each item occupies exactly one position
    for i in range(4):
        m &= island_pos.row(i).exactly_one()
        m &= export_pos.row(i).exactly_one()
        m &= attraction_pos.row(i).exactly_one()

    # Each position has exactly one of each category
    for p in range(4):
        m &= (sum(island_pos[i][p] for i in range(4)) == 1)
        m &= (sum(export_pos[i][p] for i in range(4)) == 1)
        m &= (sum(attraction_pos[i][p] for i in range(4)) == 1)

    # Constraint 1: koala (attraction 3) is south of Pwana (island 0)
    # Valid pairs: (0,2) or (1,3)
    c1_b1 = m.bool("c1_valid_pair1")  # island[0] at pos 0 AND attraction[3] at pos 2
    c1_b2 = m.bool("c1_valid_pair2")  # island[0] at pos 1 AND attraction[3] at pos 3
    m &= (c1_b1 <= island_pos[0][0])
    m &= (c1_b1 <= attraction_pos[3][2])
    m &= (c1_b1 >= island_pos[0][0] + attraction_pos[3][2] - 1)
    m &= (c1_b2 <= island_pos[0][1])
    m &= (c1_b2 <= attraction_pos[3][3])
    m &= (c1_b2 >= island_pos[0][1] + attraction_pos[3][3] - 1)
    m &= (c1_b1 | c1_b2)  # At least one valid pair

    # Constraint 2: alabaster (export 0) is west of Quero (island 1)
    # Valid pairs: (0,1) or (2,3)
    c2_b1 = m.bool("c2_valid_pair1")
    c2_b2 = m.bool("c2_valid_pair2")
    m &= (c2_b1 <= export_pos[0][0])
    m &= (c2_b1 <= island_pos[1][1])
    m &= (c2_b1 >= export_pos[0][0] + island_pos[1][1] - 1)
    m &= (c2_b2 <= export_pos[0][2])
    m &= (c2_b2 <= island_pos[1][3])
    m &= (c2_b2 >= export_pos[0][2] + island_pos[1][3] - 1)
    m &= (c2_b1 | c2_b2)

    # Constraint 3: hotel (attraction 0) is east of durian (export 3)
    # Valid pairs: (0,1) or (2,3)
    c3_b1 = m.bool("c3_valid_pair1")
    c3_b2 = m.bool("c3_valid_pair2")
    m &= (c3_b1 <= export_pos[3][0])
    m &= (c3_b1 <= attraction_pos[0][1])
    m &= (c3_b1 >= export_pos[3][0] + attraction_pos[0][1] - 1)
    m &= (c3_b2 <= export_pos[3][2])
    m &= (c3_b2 <= attraction_pos[0][3])
    m &= (c3_b2 >= export_pos[3][2] + attraction_pos[0][3] - 1)
    m &= (c3_b1 | c3_b2)

    # Constraint 4: Skern (island 3) and jai_alai (attraction 2) connected by north-south
    # Valid pairs: (0,2), (2,0), (1,3), (3,1)
    c4_bools = []
    for idx, (pos_i, pos_a) in enumerate([(0,2), (2,0), (1,3), (3,1)]):
        cb = m.bool(f"c4_pair{idx}")
        m &= (cb <= island_pos[3][pos_i])
        m &= (cb <= attraction_pos[2][pos_a])
        m &= (cb >= island_pos[3][pos_i] + attraction_pos[2][pos_a] - 1)
        c4_bools.append(cb)
    # At least one must be true
    m &= (sum(c4_bools) >= 1)

    # Constraint 5: Rayou (island 2) and bananas (export 1) connected by east-west
    # Valid pairs: (0,1), (1,0), (2,3), (3,2)
    c5_bools = []
    for idx, (pos_i, pos_e) in enumerate([(0,1), (1,0), (2,3), (3,2)]):
        cb = m.bool(f"c5_pair{idx}")
        m &= (cb <= island_pos[2][pos_i])
        m &= (cb <= export_pos[1][pos_e])
        m &= (cb >= island_pos[2][pos_i] + export_pos[1][pos_e] - 1)
        c5_bools.append(cb)
    # At least one must be true
    m &= (sum(c5_bools) >= 1)

    # Constraint 6: ice_skating (attraction 1) and jai_alai (attraction 2) NOT connected
    # Invalid pairs (adjacent): (0,1), (1,0), (0,2), (2,0), (1,3), (3,1), (2,3), (3,2)
    c6_invalid_bools = []
    for idx, (pos_a1, pos_a2) in enumerate([(0,1), (1,0), (0,2), (2,0), (1,3), (3,1), (2,3), (3,2)]):
        cb = m.bool(f"c6_invalid{idx}")
        m &= (cb <= attraction_pos[1][pos_a1])
        m &= (cb <= attraction_pos[2][pos_a2])
        m &= (cb >= attraction_pos[1][pos_a1] + attraction_pos[2][pos_a2] - 1)
        c6_invalid_bools.append(cb)
    # None of the invalid pairs should be true
    m &= (sum(c6_invalid_bools) == 0)

    # Convert boolean matrices to integer output
    island_out = m.int_vector("island_out", 4, 0, 3)
    for i in range(4):
        for p in range(4):
            m &= (island_pos[i][p] <= (island_out[i] == p))
            m &= ((island_out[i] == p) <= island_pos[i][p])

    export_out = m.int_vector("export_out", 4, 0, 3)
    for i in range(4):
        for p in range(4):
            m &= (export_pos[i][p] <= (export_out[i] == p))
            m &= ((export_out[i] == p) <= export_pos[i][p])

    attraction_out = m.int_vector("attraction_out", 4, 0, 3)
    for i in range(4):
        for p in range(4):
            m &= (attraction_pos[i][p] <= (attraction_out[i] == p))
            m &= ((attraction_out[i] == p) <= attraction_pos[i][p])

    return m, {"island": island_out, "export": export_out, "attraction": attraction_out}
