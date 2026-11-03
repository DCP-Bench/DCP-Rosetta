"""Building blocks: put the letters on the sides of the blocks so that every listed word can be spelled at once."""
import hexaly.optimizer as hx


def build(instance):
    num_blocks, num_sides = instance["num_blocks"], instance["num_sides"]
    alphabet, words = instance["alphabet"], instance["words_str"]
    index = {letter: i for i, letter in enumerate(alphabet)}
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # dice[l] is the block (0-based) that carries letter l of the alphabet
    dice = [model.int(0, num_blocks - 1) for _ in alphabet]

    # Every block has one letter on each of its sides
    for b in range(num_blocks):
        model.constraint(model.sum(d == b for d in dice) == num_sides)
    # The letters of a word sit on different blocks, so the word can be spelled
    for word in words:
        letters = [index[c] for c in word]
        for a in range(len(letters)):
            for c in range(a + 1, len(letters)):
                model.constraint(dice[letters[a]] != dice[letters[c]])

    return optimizer, {"dice": dice}
