"""SEND + MORE = MONEY with a Boolean per (letter, digit).

Every letter is one digit and every digit is used once, written as linear sums over Booleans; the sum is one
equation per column with a small carry. Hexaly proves that this is the only solution, which a permutation list
does not give it.
"""
import hexaly.optimizer as hx

LETTERS = "SENDMORY"
FIRST, SECOND, TOTAL = "SEND", "MORE", "MONEY"

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 20
    model = optimizer.model

    # is_digit[letter][d] = 1 if the letter stands for the digit d
    is_digit = {letter: [model.bool() for _ in range(10)] for letter in LETTERS}
    for letter in LETTERS:
        model.constraint(model.sum(is_digit[letter]) == 1)   # a letter is one digit
    for d in range(10):
        # a digit is used at most once (eight letters, ten digits)
        model.constraint(model.sum(is_digit[letter][d] for letter in LETTERS) <= 1)
    # No number starts with a zero (a word of one letter may be 0, so skip those)
    for word in (FIRST, SECOND, TOTAL):
        if len(word) > 1:
            model.constraint(is_digit[word[0]][0] == 0)
    digit = {letter: model.sum(d * is_digit[letter][d] for d in range(10)) for letter in LETTERS}

    # Add column by column, as on paper: carry[k] is what column k from the right passes on, 0 or 1 for two words
    # (with more words it reaches the number of words minus 1)
    columns = len(TOTAL)
    carry = [model.int(0, 1) for _ in range(columns)]
    for k in range(columns):
        carried_in = carry[k - 1] if k else 0
        in_column = [digit[word[-1 - k]] for word in (FIRST, SECOND) if k < len(word)]
        model.constraint(model.sum(in_column) + carried_in == digit[TOTAL[-1 - k]] + 10 * carry[k])
    model.constraint(carry[columns - 1] == 0)

    model.minimize(0)  # a feasibility problem still needs an objective
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("Status:", status.name)
    if status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL):
        print({letter: digit[letter].value for letter in LETTERS})
