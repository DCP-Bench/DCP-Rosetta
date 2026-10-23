from hermax.model import Model


def build(instance):
    # Hardcoded words sorted by length (descending) then alphabetically
    words = [
        "HOSES",   # 0
        "LASER",   # 1
        "SAILS",   # 2
        "SHEET",   # 3
        "STEER",   # 4
        "HEEL",    # 5
        "HIKE",    # 6
        "KEEL",    # 7
        "KNOT",    # 8
        "LINE",    # 9
        "AFT",     # 10
        "ALE",     # 11
        "EEL",     # 12
        "LEE",     # 13
        "TIE"      # 14
    ]

    # Hardcoded crossword structure:
    # Across clues: 1, 2, 3, 6, 7, 8 (with specific lengths)
    # Down clues: 2, 3, 4, 5, 7 (with specific lengths)
    # Clue positions and their orientations with lengths
    clues = {
        1: {"len": 4, "orient": "across"},   # KNOT
        2: {"len": 4, "orient": "across"},   # LINE
        3: {"len": 4, "orient": "across"},   # HEEL
        4: {"len": 4, "orient": "down"},     # HIKE
        5: {"len": 4, "orient": "down"},     # KEEL
        6: {"len": 5, "orient": "across"},   # STEER
        7: {"len": 5, "orient": "across"},   # LASER
        8: {"len": 5, "orient": "across"}    # HOSES
    }

    # Shared cells: which clues share which letter positions
    # (for enforcing consistency across intersections)
    intersections = [
        (1, 0, 2, 0),  # clue 1 pos 0 = clue 2 pos 0
        (1, 2, 3, 0),  # clue 1 pos 2 = clue 3 pos 0
        (2, 0, 4, 1),  # clue 2 pos 0 = clue 4 pos 1
        (2, 2, 5, 1),  # clue 2 pos 2 = clue 5 pos 1
        (3, 0, 6, 0),  # clue 3 pos 0 = clue 6 pos 0
        (3, 2, 7, 0),  # clue 3 pos 2 = clue 7 pos 0
        (6, 0, 8, 0),  # clue 6 pos 0 = clue 8 pos 0
        (7, 2, 8, 2),  # clue 7 pos 2 = clue 8 pos 2
    ]

    m = Model()

    # Variables: which word index is selected for each clue (1-8)
    # We need exactly 8 different words from the 15 candidates
    selected = m.int_vector("E", 8, 0, 14)

    # All selected words must be different
    m &= selected.all_different()

    # Constraint: each clue must have a word of the correct length
    for clue_num, clue_info in clues.items():
        word_idx = selected[clue_num - 1]
        # The word at word_idx must have length clue_info["len"]
        # Create constraint that word_idx matches its required length
        for w_idx, word in enumerate(words):
            if len(word) != clue_info["len"]:
                # This word cannot be selected for this clue
                m &= (word_idx != w_idx)

    # Constraint: shared cells must have matching letters
    for clue1, pos1, clue2, pos2 in intersections:
        word_idx1 = selected[clue1 - 1]
        word_idx2 = selected[clue2 - 1]
        # words[word_idx1][pos1] == words[word_idx2][pos2]
        # For each pair of words, check if they can coexist
        for w1 in range(len(words)):
            for w2 in range(len(words)):
                if words[w1][pos1] != words[w2][pos2]:
                    # These words cannot both be selected for these positions
                    # NOT (word_idx1 == w1 AND word_idx2 == w2)
                    # Equivalent to: word_idx1 != w1 OR word_idx2 != w2
                    m &= ((word_idx1 != w1) | (word_idx2 != w2))

    return m, {"E": selected}
