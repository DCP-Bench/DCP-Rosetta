"""Addition cryptarithm: give each letter a digit 0-9 so that the addends sum to the result.

Different letters get different digits, and no word of more than one letter starts with 0.
The hard model is solved first. If it ends without a solution and without a proof
(INFEASIBLE), the sum is softened: minimising |addends - sum| with the other constraints kept,
a proven minimum above 0 proves that no assignment exists.
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
addends, result = data["addends"], data["sum"]
words = addends + [result]
letters = sorted({ch for w in words for ch in w})


def unsat():
    print(json.dumps({"status": "unsatisfiable"}))
    sys.exit(0)


# More letters than digits: no two letters may share a digit
if len(letters) > 10:
    unsat()


def solve(soft):
    with hx.HexalyOptimizer() as optimizer:
        optimizer.param.verbosity = 0
        optimizer.param.nb_threads = 4
        optimizer.param.set_gap_limit(0)
        optimizer.param.time_limit = 50
        model = optimizer.model
        digit = {ch: model.int(0, 9) for ch in letters}

        def number(word):
            return model.sum(10 ** (len(word) - 1 - k) * digit[ch] for k, ch in enumerate(word))

        # Different letters get different digits
        for a in range(len(letters)):
            for b in range(a + 1, len(letters)):
                model.constraint(digit[letters[a]] != digit[letters[b]])
        # No word of more than one letter starts with 0
        for w in words:
            if len(w) > 1:
                model.constraint(digit[w[0]] != 0)

        # The addends sum to the result
        difference = model.sum(number(w) for w in addends) - number(result)
        if soft:
            gap = model.abs(difference)
            model.minimize(gap)
        else:
            model.constraint(difference == 0)
            gap = None
            model.minimize(0)
        model.close()
        optimizer.solve()

        status = optimizer.solution.status
        found = status in (S.OPTIMAL, S.FEASIBLE)
        gap_value = gap.value if (soft and found) else None
        print(f"{'soft' if soft else 'hard'} model: {status.name}", "gap:", gap_value, file=sys.stderr)
        digits = {ch: digit[ch].value for ch in letters} if found else None
        return status, gap_value, digits


status, _, digits = solve(soft=False)
if status in (S.OPTIMAL, S.FEASIBLE):
    print(json.dumps({"digits": digits}))
elif status == S.INCONSISTENT:
    unsat()
else:
    status, gap_value, digits = solve(soft=True)
    if gap_value == 0:
        print(json.dumps({"digits": digits}))
    elif status == S.OPTIMAL or status == S.INCONSISTENT:
        unsat()
    else:
        print("no assignment found and no proof that none exists", file=sys.stderr)
