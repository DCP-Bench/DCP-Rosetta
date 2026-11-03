# csplib_011_acc_basketball_schedule: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

import itertools

import mip

# Mirror pairs of dates (1-based). The second date of a pair repeats the opponents of the first, with the venues swapped.
PAIRS = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]
# On a mirror date, home becomes away and away becomes home. A bye stays a bye.
FLIP = {"H": "A", "A": "H", "B": "B"}

# Team numbers, in the order of the statement.
CLEM, DUKE, FSU, GT, UMD, UNC, NCSTATE, UVA, WAKE = range(9)
# The traditional rival of each team. FSU has none.
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCSTATE: WAKE, WAKE: NCSTATE, UMD: UVA, UVA: UMD}


def expand(base_venues, n_dates):
    """Venue of a team on dates 1..n_dates (index d - 1), given its venue on the first date of each mirror pair."""
    seq = [None] * n_dates
    for k, (r1, r2) in enumerate(PAIRS):
        seq[r1 - 1] = base_venues[k]
        seq[r2 - 1] = FLIP[base_venues[k]]
    return seq


def max_run(seq, chars):
    """Longest run of consecutive dates whose venue is one of chars."""
    best = cur = 0
    for c in seq:
        cur = cur + 1 if c in chars else 0
        best = max(best, cur)
    return best


def pattern_ok(seq):
    """Whether a venue sequence over all dates meets the rules that every team follows."""
    # No team plays away on both last dates.
    if seq[-2] == "A" and seq[-1] == "A":
        return False
    # No more than two away matches in a row, and no more than two home matches in a row.
    if max_run(seq, "A") > 2 or max_run(seq, "H") > 2:
        return False
    # No more than three away matches or byes in a row, and no more than four home matches or byes in a row.
    if max_run(seq, "AB") > 3 or max_run(seq, "HB") > 4:
        return False
    # Over the weekends (even dates), four home, four away and one bye.
    weekends = seq[1::2]
    if weekends.count("H") != 4 or weekends.count("A") != 4 or weekends.count("B") != 1:
        return False
    # On at least two of the first five weekends, a team is home or has a bye.
    if sum(1 for d in (2, 4, 6, 8, 10) if seq[d - 1] in "HB") < 2:
        return False
    return True


def team_pattern_ok(team, seq):
    """Whether a venue sequence meets the date rules of the statement that apply to one team."""
    last = len(seq)
    g = lambda d: seq[d - 1]
    if team == UNC and g(1) == "B":  # UNC has no bye on the first date.
        return False
    if team in (CLEM, GT, WAKE, FSU) and g(1) == "A":  # Clem, FSU, GT and Wake do not play away on the first date.
        return False
    if team in (CLEM, DUKE, UMD, WAKE) and g(last) == "A":  # Clem, Duke, UMD and Wake do not play away on the last date.
        return False
    if team == WAKE and g(1) != "B":  # Wake has a bye on the first date.
        return False
    if team == WAKE and g(last - 1) == "H":  # Wake does not play at home on date 17.
        return False
    if team == DUKE and g(last - 2) != "B":  # Duke has a bye on date 16.
        return False
    if team in (FSU, NCSTATE) and g(last) == "B":  # FSU and NCSt do not have a bye on the last date.
        return False
    return True


def create_model(instance):
    """Build a timetable for a double round-robin basketball tournament: every team plays every other team
    once at home and once away over the dates, with rules on venue patterns, mirrored dates, rival matches
    and fixed fixtures."""
    n_teams = instance["n_teams"]  # the number of teams
    n_days = instance["n_days"]    # the number of dates in the schedule
    model = mip.Model(solver_name="CBC")

    # patterns[t] lists the venue sequences team t may follow. Each sequence is set by the venue
    # on the first date of every mirror pair.
    patterns = {t: [] for t in range(n_teams)}
    for base_venues in itertools.product("HAB", repeat=len(PAIRS)):
        seq = expand(base_venues, n_days)
        if not pattern_ok(seq):
            continue
        for t in range(n_teams):
            if team_pattern_ok(t, seq):
                patterns[t].append(seq)

    # fol[(t, k)] is 1 when team t follows its k-th venue sequence
    fol = {}
    for t in range(n_teams):
        for k in range(len(patterns[t])):
            fol[t, k] = model.add_var(f"f_{t}_{k}", var_type=mip.BINARY)

    base_dates = [r1 for r1, _ in PAIRS]
    mirror_of = {}
    for r1, r2 in PAIRS:
        mirror_of[r1] = r2
        mirror_of[r2] = r1

    # host[(b, i, j)] is 1 when team i hosts team j on the first date b of a mirror pair.
    # Only pairs that some venue sequence allows get a variable.
    host = {}
    for b in base_dates:
        for i in range(n_teams):
            for j in range(n_teams):
                if i == j:
                    continue
                can_home = any(seq[b - 1] == "H" for seq in patterns[i])
                can_away = any(seq[b - 1] == "A" for seq in patterns[j])
                if can_home and can_away:
                    host[b, i, j] = model.add_var(f"h_{b}_{i}_{j}", var_type=mip.BINARY)

    # The variable for team i hosting team j on date d (1-based), or None when that cannot happen.
    # On the second date of a mirror pair, the teams of the first date swap roles.
    def host18(d, i, j):
        if d in mirror_of and d not in base_dates:
            return host.get((mirror_of[d], j, i))
        return host.get((d, i, j))

    # The variables that add up to 1 when teams i and j play each other on date d.
    def meet(d, i, j):
        return [v for v in (host18(d, i, j), host18(d, j, i)) if v is not None]

    # The variable that is 1 when team i plays away at team j on date d.
    def away(d, i, j):
        return host18(d, j, i)

    # The sum that is 1 when team t has the venue symbol (H, A or B) on date d.
    def role(t, d, symbol):
        return mip.xsum(fol[t, k] for k, seq in enumerate(patterns[t]) if seq[d - 1] == symbol)

    # Each team follows exactly one of its venue sequences.
    for t in range(n_teams):
        model += mip.xsum(fol[t, k] for k in range(len(patterns[t]))) == 1

    # No two teams follow the same venue sequence.
    by_seq = {}
    for t in range(n_teams):
        for k, seq in enumerate(patterns[t]):
            by_seq.setdefault(tuple(seq), []).append(fol[t, k])
    for terms in by_seq.values():
        if len(terms) > 1:
            model += mip.xsum(terms) <= 1

    # On each base date, a team hosts a match exactly when its venue is home, and visits a match exactly when its venue is away.
    for b in base_dates:
        for i in range(n_teams):
            home_i = mip.xsum(host[b, i, j] for j in range(n_teams) if (b, i, j) in host)
            away_i = mip.xsum(host[b, j, i] for j in range(n_teams) if (b, j, i) in host)
            model += home_i == role(i, b, "H")
            model += away_i == role(i, b, "A")

    # A team hosts another only when it is home and the other team is away.
    for b in base_dates:
        for i in range(n_teams):
            for j in range(n_teams):
                if (b, i, j) in host:
                    model += host[b, i, j] <= role(i, b, "H")
                    model += host[b, i, j] <= role(j, b, "A")

    # Each pair of teams meets once on the base dates. The mirror date gives the return match.
    for i in range(n_teams):
        for j in range(i + 1, n_teams):
            model += mip.xsum(host[b, i, j] for b in base_dates if (b, i, j) in host) + mip.xsum(
                host[b, j, i] for b in base_dates if (b, j, i) in host
            ) == 1

    # Each base date has n_teams // 2 matches, one team resting.
    for b in base_dates:
        model += mip.xsum(host[b, i, j] for i in range(n_teams) for j in range(n_teams) if (b, i, j) in host) == n_teams // 2

    # On the last date, a team plays only its rival, FSU, or no one.
    for t in range(n_teams):
        if t == FSU:
            continue
        for x in range(n_teams):
            if x in (t, RIVAL[t], FSU):
                continue
            for v in meet(n_days, t, x):
                model += v == 0

    # Wake and GT play UNC and Duke at least once in dates 11 to the last date.
    for i, j in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        terms = [v for d in range(11, n_days + 1) for v in meet(d, i, j)]
        model += mip.xsum(terms) >= 1

    # A team other than UNC and Duke does not play away at UNC and then at Duke on consecutive dates, or the other way round.
    for t in range(n_teams):
        if t in (UNC, DUKE):
            continue
        for d in range(1, n_days):
            for x, y in [(UNC, DUKE), (DUKE, UNC)]:
                terms = [v for v in (away(d, t, x), away(d + 1, t, y)) if v is not None]
                if len(terms) == 2:
                    model += mip.xsum(terms) <= 1

    # A team other than UNC, Duke and Wake plays at most two of them on any three consecutive dates.
    for t in range(n_teams):
        if t in (UNC, DUKE, WAKE):
            continue
        for d in range(1, n_days - 1):
            terms = [v for k in (d, d + 1, d + 2) for x in (UNC, DUKE, WAKE) for v in meet(k, t, x)]
            model += mip.xsum(terms) <= 2

    # UNC plays Duke on the last date and on date 11, and plays Clem on date 2.
    for d, i, j in [(n_days, UNC, DUKE), (11, UNC, DUKE), (2, UNC, CLEM)]:
        model += mip.xsum(meet(d, i, j)) == 1

    # config[d][i] is the team that team i plays on day d (0-based), and i itself when it has a bye.
    # where[d][i] is 0 when team i is home, 1 when it has a bye and 2 when it is away.
    config = []
    where = []
    for d in range(1, n_days + 1):
        row_config = []
        row_where = []
        for i in range(n_teams):
            hosted = [(x, host18(d, i, x)) for x in range(n_teams) if x != i and host18(d, i, x) is not None]
            hosting = [(x, host18(d, x, i)) for x in range(n_teams) if x != i and host18(d, x, i) is not None]
            row_config.append(i + mip.xsum((x - i) * v for x, v in hosted) + mip.xsum((x - i) * v for x, v in hosting))
            home = mip.xsum(v for _, v in hosted)
            away_i = mip.xsum(v for _, v in hosting)
            row_where.append(1 - home + away_i)
        config.append(row_config)
        where.append(row_where)

    return model, {"config": config, "where": where}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
