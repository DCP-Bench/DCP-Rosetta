"""Addition cryptarithm: give each letter a digit 0-9 so that the sum of the addends, read as
decimal numbers, equals the sum word. Different letters get different digits, and no word of
more than one letter starts with 0.

The distinct digits and the leading non-zero digits are hard constraints. The equation is
soft: the model minimises |addends - sum|. Objective 0 is a solution; a proven minimum above
0 (OPTIMAL, gap limit 0) proves that no assignment exists.
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
addends, total = data["addends"], data["sum"]
words = addends + [total]

letters = []
for w in words:
    for ch in w:
        if ch not in letters:
            letters.append(ch)

if len(letters) > 10:
    # More letters than digits: no assignment gives them different digits
    print(json.dumps({"status": "unsatisfiable"}))
    sys.exit()

# Weight of each letter in (sum of the addends) - (sum word)
weight = {ch: 0 for ch in letters}
for w in addends:
    for k, ch in enumerate(reversed(w)):
        weight[ch] += 10 ** k
for k, ch in enumerate(reversed(total)):
    weight[ch] -= 10 ** k
leading = {w[0] for w in words if len(w) > 1}

with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)  # a positive minimum must be proven exactly
    param.time_limit = 90
    model = optimizer.model
    # No word of more than one letter starts with 0
    digit = {ch: model.int(1 if ch in leading else 0, 9) for ch in letters}

    # Different letters get different digits
    for a in range(len(letters)):
        for b in range(a + 1, len(letters)):
            model.constraint(digit[letters[a]] != digit[letters[b]])

    # The addends sum to the sum word (soft: the amount by which they miss it)
    miss = model.abs(model.sum(weight[ch] * digit[ch] for ch in letters))
    model.minimize(miss)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    if status in (S.OPTIMAL, S.FEASIBLE) and miss.value == 0:
        print(json.dumps({"digits": {ch: digit[ch].value for ch in letters}}))
    elif status == S.INCONSISTENT or (status == S.OPTIMAL and miss.value > 0):
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print(f"undecided: {status.name}", file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        print(f"status {status.name} miss {miss.value}", file=sys.stderr)
    else:
        print(f"status {status.name}", file=sys.stderr)
