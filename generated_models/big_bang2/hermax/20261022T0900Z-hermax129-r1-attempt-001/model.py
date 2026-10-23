from hermax.model import Model


def build(instance):
    m = Model()

    # Create 5 dice: Rock(0), Paper(1), Scissors(2), Lizard(3), Spock(4)
    # Each die has 6 faces with values 1-12
    dice = m.int_matrix("dice", 5, 6, 1, 12)

    # Define beating relationships
    # Each tuple (A, B) means die A should beat die B
    beats_relationships = [
        (0, 2),  # Rock beats Scissors
        (0, 3),  # Rock beats Lizard
        (1, 0),  # Paper beats Rock
        (1, 4),  # Paper beats Spock
        (2, 1),  # Scissors beats Paper
        (2, 3),  # Scissors beats Lizard
        (3, 1),  # Lizard beats Paper
        (3, 4),  # Lizard beats Spock
        (4, 0),  # Spock beats Rock
        (4, 2),  # Spock beats Scissors
    ]

    # For each beating relationship, ensure die A beats die B in more than half the pairs
    # More than half of 36 pairs = at least 19 pairs
    for A, B in beats_relationships:
        # Create binary variables to track which pairs (face_A, face_B) satisfy face_A > face_B
        pair_beats = m.bool_matrix(f"pair_beats_{A}_{B}", 6, 6)

        # Link binary variables to actual comparisons
        for i in range(6):
            for j in range(6):
                m &= (pair_beats[i][j] == (dice[A][i] > dice[B][j]))

        # Count how many pairs A beats B (sum of binary variables)
        count_A_beats_B = m.sum_var(pair_beats.flatten())

        # Ensure A beats B in at least 19 out of 36 pairs (strictly more than half)
        m &= (count_A_beats_B > 18)

    return m, {"dice": dice}
