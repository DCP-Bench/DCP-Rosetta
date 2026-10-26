"""Addition cryptarithm with Yices.

Assign a distinct digit 0-9 to each letter so that the sum of the addends
equals the sum word when every word is read as a decimal number. No word of
more than one letter starts with 0.
"""
import json
import sys
from pathlib import Path

from yices import Context, Model, Status, Terms, Types

inst = json.loads(Path(sys.argv[1]).read_text())
addends = inst["addends"]
sum_word = inst["sum"]
words = addends + [sum_word]

letters = sorted({ch for w in words for ch in w})
INT = Types.int_type()
digit = {ch: Terms.new_uninterpreted_term(INT, f"d_{ch}") for ch in letters}
zero = Terms.integer(0)
nine = Terms.integer(9)

ctx = Context()

# Each letter is a digit from 0 to 9.
for ch in letters:
    ctx.assert_formula(Terms.arith_geq_atom(digit[ch], zero))
    ctx.assert_formula(Terms.arith_leq_atom(digit[ch], nine))

# Different letters get different digits.
if len(letters) > 1:
    ctx.assert_formula(Terms.distinct([digit[ch] for ch in letters]))

# No word longer than one letter starts with 0.
for w in words:
    if len(w) > 1:
        ctx.assert_formula(Terms.arith_gt_atom(digit[w[0]], zero))


def word_value(w):
    """The decimal value of word w as a linear term over its letters."""
    n = len(w)
    return Terms.sum([Terms.mul(Terms.integer(10 ** (n - 1 - p)), digit[ch])
                      for p, ch in enumerate(w)])


# The addends sum to the sum word.
ctx.assert_formula(Terms.arith_eq_atom(
    Terms.sum([word_value(a) for a in addends]), word_value(sum_word)))

if ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    digits = {ch: model.get_value(digit[ch]) for ch in letters}
    model.dispose()
    print(json.dumps({"digits": digits}))
else:
    print(json.dumps({"status": "unsatisfiable"}))
ctx.dispose()
