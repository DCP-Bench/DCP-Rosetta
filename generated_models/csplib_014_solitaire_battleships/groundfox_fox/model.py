# csplib_014_solitaire_battleships: a FOX model for GroundFOX from DCP Rosetta.
#
# The Battleships puzzle is played on a grid. The fleet consists of battleships (four grid
# squares in length), cruisers (three grid squares long), destroyers (two squares long) and
# submarines (one square each). The ships may be oriented horizontally or vertically, and no
# two ships will occupy adjacent grid squares, not even diagonally. The digits along the right
# side of and below the grid indicate the number of grid squares in the corresponding rows and
# columns that are occupied by vessels. In some puzzles, one or more `shots` have been taken
# to start you off. These may show water, a complete submarine, or a part of a longer vessel.
# The goal is to find the grid, where each cell is one of: water, submarine, or ship part
# (left, right, top, bottom, middle).
#
# Print the solution (grid) as a list of lists of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_014_solitaire_battleships.json --check

# Solitaire battleships: a grid cell is water, a submarine (CIRCLE), or a ship part
# (LEFT, RIGHT, TOP, BOTTOM, MIDDLE). Ships are straight, do not touch (even diagonally),
# the row and column counts of occupied cells are given, and the fleet has a fixed number
# of ships of each length (ships of length 1..4 are the submarines .. battleships).

MAX_LEN = 4
FLEET_LENGTH_FIRST = True   # fleet pair is (length, count); the other order is (count, length)
TYPES = [("W", "CW", "WATER"), ("C", "CC", "CIRCLE"), ("L", "CL", "LEFT"), ("R", "CR", "RIGHT"),
         ("T", "CT", "TOP"), ("B", "CB", "BOTTOM"), ("M", "CM", "MIDDLE")]


def _build_fox():
    inputs = ["Idx/1", "Jdx/1", "PosI/1", "PosJ/1", "Num/1", "Succ/2", "Zero/1", "Code/1",
              "Hint/3", "Rt/4", "Lf/4", "Dn/4", "Up/4", "Dg/4",
              "NoRt/2", "NoLf/2", "NoDn/2", "NoUp/2",
              "NextC/4", "Cellx/2", "EndCell/2", "EndJ/1", "EndI/1",
              "RowWant/2", "ColWant/2"]
    inputs += ["%s/1" % cn for _t, cn, _name in TYPES]
    for q in range(2, MAX_LEN + 1):
        for k in range(1, q):
            inputs += ["Sr%d_%d/4" % (q, k), "Sd%d_%d/4" % (q, k)]
        inputs += ["NoH%d/2" % q, "NoV%d/2" % q]
    for q in range(1, MAX_LEN + 1):
        inputs += ["CntQ%d/1" % q, "WantQ%d/1" % q]
    outs = ["grid/3"]
    outs += ["t%s/2" % t for t, _cn, _name in TYPES]
    outs += ["Hm/2", "Vm/2"]
    for q in range(2, MAX_LEN + 1):
        outs += ["H%d/2" % q, "V%d/2" % q]
    for q in range(1, MAX_LEN + 1):
        outs += ["St%d/2" % q, "SQ%d/3" % q]
    outs += ["RS/3", "CS/3"]

    lines = ["invocabulary { " + " ".join(inputs) + " }",
             "outvocabulary { " + " ".join(outs) + " }",
             "theory {"]
    I, J = "Idx(i)", "Jdx(j)"
    # every cell has exactly one code
    lines.append("    ! i [%s] : ! j [%s] : ? c [Code(c)] : grid(i, j, c)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! c [Code(c)] : ! d [Code(d) & c ~= d] : ~grid(i, j, c) | ~grid(i, j, d)." % (I, J))
    lines.append("    ! i : ! j : ! c [Hint(i, j, c)] : grid(i, j, c).")
    # the type literals
    for t, cn, _name in TYPES:
        lines.append("    ! i [%s] : ! j [%s] : ! c [%s(c)] : t%s(i, j) | ~grid(i, j, c)." % (I, J, cn, t))
        lines.append("    ! i [%s] : ! j [%s] : ! c [%s(c)] : ~t%s(i, j) | grid(i, j, c)." % (I, J, cn, t))
    # no two occupied cells touch diagonally
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Dg(i, j, i2, j2)] : "
                 "tW(i, j) | tW(i2, j2)." % (I, J))
    # orthogonal neighbours of occupied cells: left part of a horizontal ship, right part, etc.
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Rt(i, j, i2, j2)] : "
                 "tW(i, j) | tW(i2, j2) | tL(i, j) | tM(i, j)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Rt(i, j, i2, j2)] : "
                 "tW(i, j) | tW(i2, j2) | tM(i2, j2) | tR(i2, j2)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Dn(i, j, i2, j2)] : "
                 "tW(i, j) | tW(i2, j2) | tT(i, j) | tM(i, j)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Dn(i, j, i2, j2)] : "
                 "tW(i, j) | tW(i2, j2) | tM(i2, j2) | tB(i2, j2)." % (I, J))
    # ends of ships need their continuation
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Rt(i, j, i2, j2)] : "
                 "~tL(i, j) | tM(i2, j2) | tR(i2, j2)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Lf(i, j, i2, j2)] : "
                 "~tR(i, j) | tM(i2, j2) | tL(i2, j2)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Dn(i, j, i2, j2)] : "
                 "~tT(i, j) | tM(i2, j2) | tB(i2, j2)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Up(i, j, i2, j2)] : "
                 "~tB(i, j) | tM(i2, j2) | tT(i2, j2)." % (I, J))
    lines.append("    ! i [%s] : ! j [Jdx(j) & NoRt(i, j)] : ~tL(i, j)." % I)
    lines.append("    ! i [%s] : ! j [Jdx(j) & NoLf(i, j)] : ~tR(i, j)." % I)
    lines.append("    ! i [Idx(i)] : ! j [Jdx(j) & NoDn(i, j)] : ~tT(i, j).")
    lines.append("    ! i [Idx(i)] : ! j [Jdx(j) & NoUp(i, j)] : ~tB(i, j).")
    # a middle part is part of a horizontal or a vertical ship
    lines.append("    ! i [%s] : ! j [%s] : ~tM(i, j) | Hm(i, j) | Vm(i, j)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Lf(i, j, i2, j2)] : "
                 "~Hm(i, j) | tL(i2, j2) | tM(i2, j2)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Rt(i, j, i2, j2)] : "
                 "~Hm(i, j) | tM(i2, j2) | tR(i2, j2)." % (I, J))
    lines.append("    ! i [%s] : ! j [Jdx(j) & NoLf(i, j)] : ~Hm(i, j)." % I)
    lines.append("    ! i [%s] : ! j [Jdx(j) & NoRt(i, j)] : ~Hm(i, j)." % I)
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Up(i, j, i2, j2)] : "
                 "~Vm(i, j) | tT(i2, j2) | tM(i2, j2)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! i2 [Idx(i2)] : ! j2 [Jdx(j2) & Dn(i, j, i2, j2)] : "
                 "~Vm(i, j) | tM(i2, j2) | tB(i2, j2)." % (I, J))
    lines.append("    ! i [Idx(i)] : ! j [Jdx(j) & NoUp(i, j)] : ~Vm(i, j).")
    lines.append("    ! i [Idx(i)] : ! j [Jdx(j) & NoDn(i, j)] : ~Vm(i, j).")

    # ship starts of each length: a horizontal (H) or vertical (V) run of exactly q cells
    lines.append("    ! i [%s] : ! j [%s] : ~St1(i, j) | tC(i, j)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : St1(i, j) | ~tC(i, j)." % (I, J))
    for q in range(2, MAX_LEN + 1):
        # H_q(i, j): LEFT, MIDDLE*(q-2), RIGHT running right from (i, j)
        lines.append("    ! i [%s] : ! j [Jdx(j) & NoH%d(i, j)] : ~H%d(i, j)." % (I, q, q))
        lines.append("    ! i [Idx(i)] : ! j [Jdx(j) & NoV%d(i, j)] : ~V%d(i, j)." % (q, q))
        lines.append("    ! i [%s] : ! j [%s] : ~H%d(i, j) | tL(i, j)." % (I, J, q))
        lines.append("    ! i [%s] : ! j [%s] : ~V%d(i, j) | tT(i, j)." % (I, J, q))
        for k in range(1, q):
            mid = "tR" if k == q - 1 else "tM"
            midv = "tB" if k == q - 1 else "tM"
            lines.append("    ! i [%s] : ! j [%s] : ! a [Idx(a)] : ! b [Jdx(b) & Sr%d_%d(i, j, a, b)] : "
                         "~H%d(i, j) | %s(a, b)." % (I, J, q, k, q, mid))
            lines.append("    ! i [%s] : ! j [%s] : ! a [Idx(a)] : ! b [Jdx(b) & Sd%d_%d(i, j, a, b)] : "
                         "~V%d(i, j) | %s(a, b)." % (I, J, q, k, q, midv))
        # backward: the cells form such a run
        chain_h = ["! a%d [Idx(a%d)] : ! b%d [Jdx(b%d) & Sr%d_%d(i, j, a%d, b%d)]"
                   % (k, k, k, k, q, k, k, k) for k in range(1, q)]
        chain_v = ["! a%d [Idx(a%d)] : ! b%d [Jdx(b%d) & Sd%d_%d(i, j, a%d, b%d)]"
                   % (k, k, k, k, q, k, k, k) for k in range(1, q)]
        lits_h = ["~tM(a%d, b%d)" % (k, k) for k in range(1, q - 1)] + ["~tR(a%d, b%d)" % (q - 1, q - 1)]
        lits_v = ["~tM(a%d, b%d)" % (k, k) for k in range(1, q - 1)] + ["~tB(a%d, b%d)" % (q - 1, q - 1)]
        lines.append("    ! i [%s] : ! j [%s] : %s : H%d(i, j) | ~tL(i, j) | %s." % (
            I, J, " : ".join(chain_h), q, " | ".join(lits_h)))
        lines.append("    ! i [%s] : ! j [%s] : %s : V%d(i, j) | ~tT(i, j) | %s." % (
            I, J, " : ".join(chain_v), q, " | ".join(lits_v)))
    for q in range(1, MAX_LEN + 1):
        if q == 1:
            lines.append("    ! i [%s] : ! j [%s] : ~St1(i, j) | tC(i, j)." % (I, J))
            continue
        lines.append("    ! i [%s] : ! j [%s] : ~St%d(i, j) | H%d(i, j) | V%d(i, j)." % (I, J, q, q, q))
        lines.append("    ! i [%s] : ! j [%s] : ~H%d(i, j) | St%d(i, j)." % (I, J, q, q))
        lines.append("    ! i [%s] : ! j [%s] : ~V%d(i, j) | St%d(i, j)." % (I, J, q, q))

    # counters along row-major cells: how many ship starts of length q so far
    for q in range(1, MAX_LEN + 1):
        lines.append("    ! z [Zero(z)] : SQ%d(z, z, z)." % q)
        lines.append("    ! i [%s] : ! j [%s] : ! i2 [PosI(i2)] : ! j2 [PosJ(j2) & NextC(i, j, i2, j2)] : "
                     "! k [CntQ%d(k)] : ! k2 [Succ(k, k2)] : ~SQ%d(i, j, k) | ~St%d(i, j) | SQ%d(i2, j2, k2)."
                     % (I, J, q, q, q, q))
        lines.append("    ! i [%s] : ! j [%s] : ! i2 [PosI(i2)] : ! j2 [PosJ(j2) & NextC(i, j, i2, j2)] : "
                     "! k [CntQ%d(k)] : ~SQ%d(i, j, k) | St%d(i, j) | SQ%d(i2, j2, k)."
                     % (I, J, q, q, q, q))
        lines.append("    ! i [PosI(i)] : ! j [PosJ(j) & Cellx(i, j)] : ? k [CntQ%d(k)] : SQ%d(i, j, k)." % (q, q))
        lines.append("    ! i [PosI(i)] : ! j [PosJ(j) & Cellx(i, j)] : ! k [CntQ%d(k)] : "
                     "! k2 [CntQ%d(k2) & k ~= k2] : ~SQ%d(i, j, k) | ~SQ%d(i, j, k2)." % (q, q, q, q))
        lines.append("    ! i [PosI(i)] : ! j [PosJ(j)] : ! k [Num(k) & ~CntQ%d(k)] : ~SQ%d(i, j, k)." % (q, q))
        lines.append("    ! i [PosI(i)] : ! j [EndCell(i, j)] : ! k [WantQ%d(k)] : SQ%d(i, j, k)." % (q, q))

    # row and column counts of occupied cells
    lines.append("    ! i [%s] : ! z [Zero(z)] : RS(i, z, z)." % I)
    lines.append("    ! i [%s] : ! j [%s] : ! j2 [PosJ(j2) & Succ(j, j2)] : ! k [Num(k)] : "
                 "~RS(i, j, k) | ~tW(i, j) | RS(i, j2, k)." % (I, J))
    lines.append("    ! i [%s] : ! j [%s] : ! j2 [PosJ(j2) & Succ(j, j2)] : ! k [Num(k)] : ! k2 [Succ(k, k2)] : "
                 "~RS(i, j, k) | tW(i, j) | RS(i, j2, k2)." % (I, J))
    lines.append("    ! i [%s] : ! j [PosJ(j)] : ? k [Num(k)] : RS(i, j, k)." % I)
    lines.append("    ! i [%s] : ! j [PosJ(j)] : ! k [Num(k)] : ! k2 [Num(k2) & k ~= k2] : "
                 "~RS(i, j, k) | ~RS(i, j, k2)." % I)
    lines.append("    ! i [%s] : ! j [EndJ(j)] : ! k [RowWant(i, k)] : RS(i, j, k)." % I)
    lines.append("    ! j [%s] : ! z [Zero(z)] : CS(j, z, z)." % J)
    lines.append("    ! j [%s] : ! i [Idx(i)] : ! i2 [PosI(i2) & Succ(i, i2)] : ! k [Num(k)] : "
                 "~CS(j, i, k) | ~tW(i, j) | CS(j, i2, k)." % J)
    lines.append("    ! j [%s] : ! i [Idx(i)] : ! i2 [PosI(i2) & Succ(i, i2)] : ! k [Num(k)] : ! k2 [Succ(k, k2)] : "
                 "~CS(j, i, k) | tW(i, j) | CS(j, i2, k2)." % J)
    lines.append("    ! j [PosJ(j)] : ! i [PosI(i)] : ? k [Num(k)] : CS(j, i, k).")
    lines.append("    ! j [PosJ(j)] : ! i [PosI(i)] : ! k [Num(k)] : ! k2 [Num(k2) & k ~= k2] : "
                 "~CS(j, i, k) | ~CS(j, i, k2).")
    lines.append("    ! j [%s] : ! i [EndI(i)] : ! k [ColWant(j, k)] : CS(j, i, k)." % J)
    lines.append("}")
    return "\n".join(lines) + "\n"


FOX = _build_fox()


def structure(instance):
    R = instance["rows"]
    C = instance["cols"]
    rowsum = instance["rowsum"]
    colsum = instance["colsum"]
    codes = {"W": instance["WATER"], "C": instance["CIRCLE"], "L": instance["LEFT"],
             "R": instance["RIGHT"], "T": instance["TOP"], "B": instance["BOTTOM"],
             "M": instance["MIDDLE"]}
    M = max(R, C) + 1

    # fleet: ship length q has want[q] ships
    want = {q: 0 for q in range(1, MAX_LEN + 1)}
    for a, b in instance["fleet_counts"]:
        length, count = (a, b) if FLEET_LENGTH_FIRST else (b, a)
        if 1 <= length <= MAX_LEN:
            want[length] += count

    # hints: (row, col, code); accept 1-based coordinates when they reach the far edge
    hints = instance.get("hints", [])
    base = 0
    if hints and max(h[0] for h in hints) == R or hints and max(h[1] for h in hints) == C:
        base = 1
    hint_rel = [(h[0] - base, h[1] - base, codes_val) for h in hints
                for codes_val in [h[2]]]

    cells = [(i, j) for i in range(R) for j in range(C)]
    inb = set(cells)

    def nb(i, j, di, dj):
        return (i + di, j + dj) in inb

    out = {
        "Idx": list(range(R)),
        "Jdx": list(range(C)),
        "PosI": list(range(R + 1)),
        "PosJ": list(range(C + 1)),
        "Num": list(range(0, M + 1)),
        "Succ": [(k, k + 1) for k in range(0, M)],
        "Zero": [0],
        "Code": list(codes.values()),
        "Hint": hint_rel,
        "Rt": [(i, j, i, j + 1) for i, j in cells if nb(i, j, 0, 1)],
        "Lf": [(i, j, i, j - 1) for i, j in cells if nb(i, j, 0, -1)],
        "Dn": [(i, j, i + 1, j) for i, j in cells if nb(i, j, 1, 0)],
        "Up": [(i, j, i - 1, j) for i, j in cells if nb(i, j, -1, 0)],
        "Dg": [(i, j, i + di, j + dj) for i, j in cells for di in (-1, 1) for dj in (-1, 1)
               if nb(i, j, di, dj)],
        "NoRt": [(i, j) for i, j in cells if not nb(i, j, 0, 1)],
        "NoLf": [(i, j) for i, j in cells if not nb(i, j, 0, -1)],
        "NoDn": [(i, j) for i, j in cells if not nb(i, j, 1, 0)],
        "NoUp": [(i, j) for i, j in cells if not nb(i, j, -1, 0)],
    }
    # cell order row-major, with a final pseudo cell (R, 0) after the last one
    order = cells + [(R, 0)]
    out["NextC"] = [(order[k][0], order[k][1], order[k + 1][0], order[k + 1][1])
                    for k in range(len(order) - 1)]
    out["Cellx"] = order
    out["EndCell"] = [(R, 0)]
    out["EndJ"] = [C]
    out["EndI"] = [R]
    out["RowWant"] = [(i, rowsum[i]) for i in range(R)]
    out["ColWant"] = [(j, colsum[j]) for j in range(C)]
    for q in range(1, MAX_LEN + 1):
        out["CntQ%d" % q] = list(range(0, want[q] + 1))
        out["WantQ%d" % q] = [want[q]]
    for _t, cn, name in TYPES:
        out[cn] = [codes[_t]]
    for q in range(2, MAX_LEN + 1):
        for k in range(1, q):
            out["Sr%d_%d" % (q, k)] = [(i, j, i, j + k) for i, j in cells if nb(i, j, 0, k)]
            out["Sd%d_%d" % (q, k)] = [(i, j, i + k, j) for i, j in cells if nb(i, j, k, 0)]
        out["NoH%d" % q] = [(i, j) for i, j in cells if not nb(i, j, 0, q - 1)]
        out["NoV%d" % q] = [(i, j) for i, j in cells if not nb(i, j, q - 1, 0)]
    return out
