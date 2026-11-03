"""Building blocks: put the letters on the sides of the blocks so that every listed word can be spelled at once."""
import hexaly.optimizer as hx


def build(instance):
    # num_blocks = how many alphabet blocks there are; num_sides = how many sides, so letters, each block has
    num_blocks, num_sides = instance["num_blocks"], instance["num_sides"]
    # alphabet = the string of letters placed on the blocks (one character per letter);
    # words_str = the words that must all be spelled with the blocks
    alphabet, words = instance["alphabet"], instance["words_str"]
    # position of each letter in the alphabet string, used to index dice
    index = {letter: i for i, letter in enumerate(alphabet)}
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # dice[l] = the block (0 to num_blocks - 1) that carries letter l of the alphabet; each letter
    # sits on one side of exactly one block
    dice = [model.int(0, num_blocks - 1) for _ in alphabet]

    # Every block has num_sides sides with one letter on each, so exactly num_sides letters sit on every block
    for b in range(num_blocks):
        model.constraint(model.sum(d == b for d in dice) == num_sides)
    # To spell a word, each of its letters must come from a different block (a block shows one letter
    # at a time), so no two letters of a word sit on the same block
    for word in words:
        letters = [index[c] for c in word]  # alphabet positions of the word's letters
        for a in range(len(letters)):
            for c in range(a + 1, len(letters)):
                model.constraint(dice[letters[a]] != dice[letters[c]])

    return optimizer, {"dice": dice}
