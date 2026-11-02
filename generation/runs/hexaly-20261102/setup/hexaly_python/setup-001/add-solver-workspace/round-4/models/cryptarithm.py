"""Addition cryptarithm: give each letter a digit 0-9 so that the sum of the addend words equals
the sum word, read as decimal numbers. Different letters get different digits, and no word of
more than one letter starts with 0.

Solved as a violation model: distinct digits and nonzero leading digits are hard, and the
objective is the absolute difference between the two sides of the addition. A proven minimum of
0 is a solution; a proven minimum above 0 proves that none exists.
Prints {"digits": {...}} or {"status": "unsatisfiable"}.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
addends, result = data["addends"], data["sum"]
words = addends + [result]
letters = list(dict.fromkeys("".join(words)))  # in order of first appearance

# Different letters get different digits: more than ten letters cannot all differ
if len(letters) > 10:
    print(json.dumps({"status": "unsatisfiable"}))
    sys.exit(0)

# Weight of each letter in (sum of addends) - (sum word), by decimal position
weight = {L: 0 for L in letters}
for w in addends:
    for k, ch in enumerate(reversed(w)):
        weight[ch] += 10 ** k
for k, ch in enumerate(reversed(result)):
    weight[ch] -= 10 ** k

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)  # a proven minimum must be exact
    optimizer.param.time_limit = 90
    model = optimizer.model
    digit = {L: model.int(0, 9) for L in letters}

    # Different letters get different digits
    for i, a in enumerate(letters):
        for b in letters[i + 1:]:
            model.constraint(digit[a] != digit[b])
    # No word of more than one letter starts with 0
    for w in words:
        if len(w) > 1:
            model.constraint(digit[w[0]] >= 1)

    # The addition holds: minimise how far the two sides are apart
    miss = model.abs(model.sum(weight[L] * digit[L] for L in letters))
    model.minimize(miss)
    model.close()
    started = time.monotonic()
    optimizer.solve()

    status = optimizer.solution.status
    value = miss.value if status in (S.OPTIMAL, S.FEASIBLE) else None
    print(f"status {status.name} miss {value} solve {time.monotonic() - started:.2f} s", file=sys.stderr)
    if status == S.INCONSISTENT or (status == S.OPTIMAL and value >= 1):
        print(json.dumps({"status": "unsatisfiable"}))
    elif status in (S.OPTIMAL, S.FEASIBLE) and value == 0:
        print(json.dumps({"digits": {L: digit[L].value for L in letters}}))
    else:
        print("undecided within the time limit", file=sys.stderr)
        sys.exit(1)
