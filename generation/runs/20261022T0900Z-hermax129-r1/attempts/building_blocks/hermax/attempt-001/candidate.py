from hermax.model import Model


def build(instance):
    # Read instance: alphabet, words, and block configuration
    alphabet = instance["alphabet"]
    words_str = instance["words_str"]
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]
    num_letters = instance["num_letters"]

    m = Model()

    # Create assignment variables: which block each letter is placed on
    # dice[i] = block number (0 to num_blocks-1) for alphabet[i]
    dice = m.int_vector("dice", num_letters, 0, num_blocks - 1)

    # Constraint: each block must have exactly num_sides letters
    # Count letters on each block using indicator variables
    for b in range(num_blocks):
        # Create binary variables for membership in block b
        in_block = m.bool_vector(f"in_block_{b}", num_letters)
        for i in range(num_letters):
            # in_block[i] is true iff dice[i] == b
            m &= (in_block[i] == (dice[i] == b))
        # Sum must equal num_sides
        m &= (sum(in_block) == num_sides)

    # Constraint: to spell each word, letters must be on different blocks
    # (each block can only show one side at a time)
    for word in words_str:
        # Find indices of letters in this word
        letter_indices = [alphabet.index(ch) for ch in word]
        # All these letters must be on different blocks
        if len(letter_indices) > 1:
            # All pairs must have different block assignments
            for i in range(len(letter_indices)):
                for j in range(i + 1, len(letter_indices)):
                    m &= (dice[letter_indices[i]] != dice[letter_indices[j]])

    return m, {"dice": dice}
