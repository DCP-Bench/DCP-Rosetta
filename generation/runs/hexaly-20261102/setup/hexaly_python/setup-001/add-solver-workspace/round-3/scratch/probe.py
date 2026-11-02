"""Scratch probe (not a deliverable): when does a hard model with no solution stop?"""
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus


def run(addends, total, limit, verbosity):
    words = addends + [total]
    letters = sorted(set("".join(words)))
    weight = {ch: 0 for ch in letters}
    for w in addends:
        for k, ch in enumerate(reversed(w)):
            weight[ch] += 10 ** k
    for k, ch in enumerate(reversed(total)):
        weight[ch] -= 10 ** k
    leading = {w[0] for w in words if len(w) > 1}
    with hx.HexalyOptimizer() as optimizer:
        param = optimizer.param
        param.verbosity = verbosity
        param.nb_threads = 4
        param.set_gap_limit(0)
        param.time_limit = limit
        model = optimizer.model
        digit = {ch: model.int(1 if ch in leading else 0, 9) for ch in letters}
        for a in range(len(letters)):
            for b in range(a + 1, len(letters)):
                model.constraint(digit[letters[a]] != digit[letters[b]])
        model.constraint(model.sum(weight[ch] * digit[ch] for ch in letters) == 0)
        model.minimize(0)
        model.close()
        t = time.monotonic()
        optimizer.solve()
        el = time.monotonic() - t
        print("limit", limit, optimizer.solution.status.name, f"{el:.2f}s", flush=True)


run(["CCEE", "GGCB"], "DHACI", 10, 1)
run(["CCEE", "GGCB"], "DHACI", 10, 0)
run(["CCEE", "GGCB"], "DHACI", 5, 0)
