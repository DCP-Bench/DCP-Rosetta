# csplib_012_nonogram: a FOX model for GroundFOX from DCP Rosetta.
#
# Nonograms are a popular puzzle, which goes by different names in different countries.
# Solvers have to shade in squares in a grid so that blocks of consecutive shaded squares
# satisfy constraints given for each row and column. Constraints typically indicate the
# sequence of shaded blocks (e.g. 3,1,2 means that there is a block of 3, then a gap of
# unspecified size, a block of length 1, another gap, and then a block of length 2).
#
# Print the solution board (board) as a list of lists of integers, where 1 represents a shaded
# square and 0 represents an unshaded square.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_012_nonogram.json --check

# csplib_012_nonogram: a FOX model for GroundFOX from DCP Rosetta.
#
# Nonogram: shade cells of a rows x cols grid so that the maximal runs of shaded
# cells in each row and column match the given block sequences (zeros are padding).
# Each line is checked by a deterministic automaton (built in structure from the
# block sequence); the automaton state at each position is a function over the
# state set, at most one state per position is enforced by a ladder over the data
# successor relation StNext.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json
FOX = """
invocabulary { Row/1 Col/1 Bin/1 St/1 StNext/2 RPos/1 RPosAll/1 RNext/2 RLast/1 CPos/1 CPosAll/1 CNext/2 CLast/1 RTr/4 CTr/4 RAcc/2 CAcc/2 RBad/2 CBad/2 }
outvocabulary { board/3 stR/3 stC/3 seenR/3 seenC/3 }
theory {
    ! r [Row(r)] : ! c [Col(c)] : ? v [Bin(v)] : board(r, c, v).
    ! r [Row(r)] : ! c [Col(c)] : ! v [Bin(v)] : ! w [Bin(w) & v ~= w] : ~board(r, c, v) | ~board(r, c, w).

    ! r [Row(r)] : stR(r, 0, 0).
    ! r [Row(r)] : ! i [RPosAll(i)] : ! s [RBad(r, s)] : ~stR(r, i, s).
    ! r [Row(r)] : ! i [RPosAll(i)] : ? s [St(s)] : stR(r, i, s).
    ! r [Row(r)] : ! i [RPosAll(i)] : ! s [St(s)] : ~stR(r, i, s) | seenR(r, i, s).
    ! r [Row(r)] : ! i [RPosAll(i)] : ! s : ! t [StNext(s, t)] : ~seenR(r, i, s) | seenR(r, i, t).
    ! r [Row(r)] : ! i [RPosAll(i)] : ! s : ! t [StNext(s, t)] : ~seenR(r, i, s) | ~stR(r, i, t).
    ! r [Row(r)] : ! i [RPos(i)] : ! j [RNext(i, j)] : ! s [St(s)] : ! b [Bin(b)] : ! t [RTr(r, s, b, t)] : ~stR(r, i, s) | ~board(r, i, b) | stR(r, j, t).
    ! r [Row(r)] : ! i [RLast(i)] : ? s [RAcc(r, s)] : stR(r, i, s).

    ! c [Col(c)] : stC(c, 0, 0).
    ! c [Col(c)] : ! i [CPosAll(i)] : ! s [CBad(c, s)] : ~stC(c, i, s).
    ! c [Col(c)] : ! i [CPosAll(i)] : ? s [St(s)] : stC(c, i, s).
    ! c [Col(c)] : ! i [CPosAll(i)] : ! s [St(s)] : ~stC(c, i, s) | seenC(c, i, s).
    ! c [Col(c)] : ! i [CPosAll(i)] : ! s : ! t [StNext(s, t)] : ~seenC(c, i, s) | seenC(c, i, t).
    ! c [Col(c)] : ! i [CPosAll(i)] : ! s : ! t [StNext(s, t)] : ~seenC(c, i, s) | ~stC(c, i, t).
    ! c [Col(c)] : ! i [CPos(i)] : ! j [CNext(i, j)] : ! s [St(s)] : ! b [Bin(b)] : ! t [CTr(c, s, b, t)] : ~stC(c, i, s) | ~board(i, c, b) | stC(c, j, t).
    ! c [Col(c)] : ! i [CLast(i)] : ? s [CAcc(c, s)] : stC(c, i, s).
}
"""


def _dfa(blocks):
    """Deterministic automaton accepting the 0/1 lines whose runs of 1s are exactly `blocks`.

    State ("G", k): k blocks finished, the next cell may start block k+1.
    State ("R", k, j): inside block k (1-based), j cells of it shaded so far.
    State id 0 is the start state. Returns (number of states, transitions, accepting ids, dead ids).
    """
    m = len(blocks)

    dead = ("X",)  # reject state: every (state, bit) pair has a successor

    def step(state, bit):
        if state == dead:
            return dead
        if state[0] == "G":
            k = state[1]
            if bit == 0:
                return ("G", k)
            return ("R", k + 1, 1) if k < m else dead
        _, k, j = state
        length = blocks[k - 1]
        if bit == 1:
            return ("R", k, j + 1) if j < length else dead
        return ("G", k) if j == length else dead

    def accepting(state):
        if state == ("G", m):
            return True
        return state[0] == "R" and state[1] == m and state[2] == blocks[m - 1]

    start = ("G", 0)
    ids = {start: 0}
    queue = [start]
    trans = []
    for state in queue:
        for bit in (0, 1):
            nxt = step(state, bit)
            if nxt not in ids:
                ids[nxt] = len(ids)
                queue.append(nxt)
            trans.append((ids[state], bit, ids[nxt]))
    acc = [ids[st] for st in queue if accepting(st)]
    # states from which no accepting state is reachable (the dead state included)
    live = set(acc)
    changed = True
    while changed:
        changed = False
        for src, _, dst in trans:
            if dst in live and src not in live:
                live.add(src)
                changed = True
    bad = [i for i in range(len(ids)) if i not in live]
    return len(ids), trans, acc, bad


def structure(instance):
    R, C = instance["rows"], instance["cols"]
    row_dfa = [_dfa([x for x in rule if x > 0]) for rule in instance["row_rules"]]
    col_dfa = [_dfa([x for x in rule if x > 0]) for rule in instance["col_rules"]]
    S = max(n for n, _, _, _ in row_dfa + col_dfa)
    return {
        "domain": list(range(max(R, C, S, 2) + 1)),
        "Row": list(range(R)),
        "Col": list(range(C)),
        "Bin": [0, 1],
        "St": list(range(S)),
        "StNext": [(s, s + 1) for s in range(S - 1)],
        "RPos": list(range(C)),
        "RPosAll": list(range(C + 1)),
        "RNext": [(i, i + 1) for i in range(C)],
        "RLast": [C],
        "CPos": list(range(R)),
        "CPosAll": list(range(R + 1)),
        "CNext": [(i, i + 1) for i in range(R)],
        "CLast": [R],
        "RTr": [(r, s, b, t) for r, (_, trans, _, _) in enumerate(row_dfa) for s, b, t in trans],
        "RAcc": [(r, s) for r, (_, _, acc, _) in enumerate(row_dfa) for s in acc],
        "RBad": [(r, s) for r, (_, _, _, bad) in enumerate(row_dfa) for s in bad],
        "CTr": [(c, s, b, t) for c, (_, trans, _, _) in enumerate(col_dfa) for s, b, t in trans],
        "CAcc": [(c, s) for c, (_, _, acc, _) in enumerate(col_dfa) for s in acc],
        "CBad": [(c, s) for c, (_, _, _, bad) in enumerate(col_dfa) for s in bad],
    }
