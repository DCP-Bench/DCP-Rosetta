# Addition cryptarithm: give each letter a distinct digit 0-9 so that the addends sum to the sum word.
# Usage: python cryptarithm.py INSTANCE.json
import json
import sys

from yices import Context, Model, Status, Terms, Types


def word_value(word, letter_term):
    # decimal value of a word as a linear term: sum of letter * 10^position
    parts = [Terms.mul(Terms.integer(10 ** pos), letter_term[ch])
             for pos, ch in enumerate(reversed(word))]
    return Terms.sum(parts)


def main():
    inst = json.load(open(sys.argv[1]))
    addends = inst["addends"]
    total = inst["sum"]
    letters = sorted(set("".join(addends) + total))

    INT = Types.int_type()
    letter_term = {ch: Terms.new_uninterpreted_term(INT, ch) for ch in letters}

    ctx = Context()
    # each letter is a digit
    for ch in letters:
        ctx.assert_formula(Terms.arith_geq_atom(letter_term[ch], Terms.integer(0)))
        ctx.assert_formula(Terms.arith_leq_atom(letter_term[ch], Terms.integer(9)))
    # different letters get different digits
    if len(letters) > 1:
        ctx.assert_formula(Terms.distinct([letter_term[ch] for ch in letters]))
    # no multi-letter word starts with 0
    for word in addends + [total]:
        if len(word) > 1:
            ctx.assert_formula(Terms.arith_geq_atom(letter_term[word[0]], Terms.integer(1)))
    # the addends sum to the sum word
    lhs = Terms.sum([word_value(w, letter_term) for w in addends])
    ctx.assert_formula(Terms.arith_eq_atom(lhs, word_value(total, letter_term)))

    if ctx.check_context() != Status.SAT:
        print(json.dumps({"status": "unsatisfiable"}))
        return
    model = Model.from_context(ctx, 1)
    digits = {ch: model.get_value(letter_term[ch]) for ch in letters}
    model.dispose()
    ctx.dispose()
    print(json.dumps({"digits": digits}))


if __name__ == "__main__":
    main()
