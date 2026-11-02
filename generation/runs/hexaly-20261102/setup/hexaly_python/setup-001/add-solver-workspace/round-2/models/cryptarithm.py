"""Addition cryptarithm: give each letter a digit 0-9 so that the sum of the addend words
equals the sum word read as decimal numbers; different letters get different digits and no
word of more than one letter starts with 0.

An integer digit per letter, pairwise != for different letters, one linear equation.
First solved with hard constraints: a solution, or INCONSISTENT (a proof that none exists).
If that ends INFEASIBLE (nothing found, no proof), the equation is moved into the objective
as |left - right|; a proven minimum above 0 proves that no assignment exists.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus
START = time.monotonic()
BUDGET = 90  # seconds for the whole program
HARD_LIMIT = 20  # seconds for the hard model before the violation-minimising one


def time_left():
    return max(1, int(BUDGET - (time.monotonic() - START)))


with open(sys.argv[1]) as f:
    data = json.load(f)
addends, total_word = data["addends"], data["sum"]
words = addends + [total_word]
letters = sorted({ch for w in words for ch in w})
leading = {w[0] for w in words if len(w) > 1}

if len(letters) > 10:  # more letters than digits: they cannot all differ
    print(json.dumps({"status": "unsatisfiable"}))
    sys.exit(0)


def word_value(model, digit, w):
    return model.sum(10 ** (len(w) - 1 - i) * digit[ch] for i, ch in enumerate(w))


def build(optimizer, soft, time_limit):
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = time_limit
    model = optimizer.model
    digit = {ch: model.int(1 if ch in leading else 0, 9) for ch in letters}
    # (the domain 1-9 for a leading letter: no word of more than one letter starts with 0)

    # Different letters get different digits
    for i, a in enumerate(letters):
        for b in letters[i + 1:]:
            model.constraint(digit[a] != digit[b])

    # The addition holds
    left = model.sum(word_value(model, digit, w) for w in addends)
    right = word_value(model, digit, total_word)
    if soft:
        # |left - right| as two non-negative parts
        bound = sum(10 ** len(w) for w in words)
        over, under = model.int(0, bound), model.int(0, bound)
        model.constraint(left - right == over - under)
        error = over + under
        model.minimize(error)
    else:
        model.constraint(left == right)
        error = None
        model.minimize(0)
    model.close()
    optimizer.solve()
    return optimizer.solution.status, digit, error


def report(digit):
    print(json.dumps({"digits": {ch: digit[ch].value for ch in letters}}))


with hx.HexalyOptimizer() as optimizer:
    status, digit, _ = build(optimizer, soft=False, time_limit=min(HARD_LIMIT, time_left()))
    print("hard model:", status.name, file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        report(digit)
        sys.exit(0)
    if status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
        sys.exit(0)

# Nothing found and nothing proven: minimise how far the addition is from holding
with hx.HexalyOptimizer() as optimizer:
    status, digit, error = build(optimizer, soft=True, time_limit=time_left())
    print("soft model:", status.name, file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE) and error.value == 0:
        report(digit)
    elif status == S.OPTIMAL or status == S.INCONSISTENT:
        # proven: the addition cannot hold
        if status == S.OPTIMAL:
            print("minimum |left - right|:", error.value, file=sys.stderr)
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print("no proof either way", file=sys.stderr)
