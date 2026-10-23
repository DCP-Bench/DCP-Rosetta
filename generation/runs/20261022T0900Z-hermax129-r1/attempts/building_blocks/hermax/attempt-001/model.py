from hermax.model import Model


def build(instance):
    # Read instance: alphabet, words, and block configuration
    alphabet = instance["alphabet"]
    words_str = instance["words_str"]
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]
    num_letters = instance["num_letters"]

    m = Model()

    # Assignment variables: which block each letter is placed on
    # Output represents the mapping from alphabet to blocks
    dice = m.int_vector("dice", num_letters, 0, num_blocks - 1)

    # Constraint group 1: partition letters across blocks
    # Each block must have exactly num_sides letters (6 sides per block)
    for b in range(num_blocks):
        in_block = m.bool_vector(f"in_block_{b}", num_letters)
        for i in range(num_letters):
            # Indicator: in_block[i] iff dice[i] == b
            m &= (in_block[i] == (dice[i] == b))
        # Sum must equal num_sides
        m &= (sum(in_block) == num_sides)

    # Constraint group 2: word constraints
    # To spell each word, letters must be on different blocks
    # (each block can show only one orientation at a time)
    for word in words_str:
        letter_indices = [alphabet.index(ch) for ch in word]
        if len(letter_indices) > 1:
            # All letter pairs in a word must be on different blocks
            for i in range(len(letter_indices)):
                for j in range(i + 1, len(letter_indices)):
                    m &= (dice[letter_indices[i]] != dice[letter_indices[j]])

    return m, {"dice": dice}
