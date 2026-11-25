# kenken: a FOX model for GroundFOX from DCP Rosetta.
#
# KenKen or KEN-KEN is a style of arithmetic and logical puzzle sharing several
# characteristics with sudoku. The name comes from Japanese and is translated as 'square
# wisdom' or 'cleverness squared'.
#
# The objective is to fill the grid in with the digits 1 through 6 such that:
#
# * Each row contains exactly one of each digit * Each column contains exactly one of each
# digit * Each bold-outlined group of cells is a cage containing digits which achieve the
# specified result using the specified mathematical operation: addition (+), subtraction (-),
# multiplication (x), and division (/). (Unlike in Killer sudoku, digits may repeat within a
# group.)
#
# More complex KenKen problems are formed using the principles described above but omitting
# the symbols +, -, x and /, thus leaving them as yet another unknown to be determined. This
# is such a problem: `problem` lists each cage as its result and its cells, each cell being a
# 1-based [row, column]. A cage of one cell holds its result. A cage of two cells may use any
# of the four operations, and a division must be exact. A larger cage uses either addition or
# multiplication.
#
# Print the solved grid (x) as a list of lists of integers ranging from 1 to 6.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py kenken.json --check

# kenken: a GroundFOX model of a KenKen grid of size n with unknown cage operations.
# x(r, c, v): cell (r, c) (0-based) holds digit v in 1..n. Rows and columns are all-different.
# Each cage (given as its result and its 1-based cells) is a relation over the digits of its cells,
# computed as data in structure(): one digit for a single cell, the pairs whose sum, difference,
# product or exact quotient is the result for two cells, and the tuples whose sum or product is the
# result for three to five cells. The cells of cage k are the slots Sl0..Sl4 of k.

FOX = """
invocabulary { Row/1 Col/1 Val/1 Cell/1 Rw/2 Cl/2 Ar1/1 Ar2/1 Ar3/1 Ar4/1 Ar5/1 Sl0/2 Sl1/2 Sl2/2 Sl3/2 Sl4/2 A1/2 A2/3 A3/4 A4/5 A5/6 }
outvocabulary { x/3 }
theory {
    ! r [Row(r)] : ! c [Col(c)] : ? v [Val(v)] : x(r, c, v).
    ! r [Row(r)] : ! c [Col(c)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~x(r, c, v) | ~x(r, c, w).
    ! r [Row(r)] : ! v [Val(v)] : ? c [Col(c)] : x(r, c, v).
    ! r [Row(r)] : ! v [Val(v)] : ! c [Col(c)] : ! d [Col(d) & c ~= d] : ~x(r, c, v) | ~x(r, d, v).
    ! c [Col(c)] : ! v [Val(v)] : ? r [Row(r)] : x(r, c, v).
    ! c [Col(c)] : ! v [Val(v)] : ! r [Row(r)] : ! s [Row(s) & r ~= s] : ~x(r, c, v) | ~x(s, c, v).

    ! k [Ar1(k)] : ! v [Val(v) & ~A1(k, v)] : ! i [Sl0(k, i)] : ! r [Rw(i, r)] : ! c [Cl(i, c)] : ~x(r, c, v).

    ! k [Ar2(k)] : ! v1 [Val(v1)] : ! v2 [Val(v2) & ~A2(k, v1, v2)] : ! i [Sl0(k, i)] : ! r [Rw(i, r)] : ! c [Cl(i, c)] : ! j [Sl1(k, j)] : ! s [Rw(j, s)] : ! d [Cl(j, d)] : ~x(r, c, v1) | ~x(s, d, v2).

    ! k [Ar3(k)] : ! v1 [Val(v1)] : ! v2 [Val(v2)] : ! v3 [Val(v3) & ~A3(k, v1, v2, v3)] : ! i [Sl0(k, i)] : ! r [Rw(i, r)] : ! c [Cl(i, c)] : ! j [Sl1(k, j)] : ! s [Rw(j, s)] : ! d [Cl(j, d)] : ! t [Sl2(k, t)] : ! u [Rw(t, u)] : ! e [Cl(t, e)] : ~x(r, c, v1) | ~x(s, d, v2) | ~x(u, e, v3).

    ! k [Ar4(k)] : ! v1 [Val(v1)] : ! v2 [Val(v2)] : ! v3 [Val(v3)] : ! v4 [Val(v4) & ~A4(k, v1, v2, v3, v4)] : ! i [Sl0(k, i)] : ! r [Rw(i, r)] : ! c [Cl(i, c)] : ! j [Sl1(k, j)] : ! s [Rw(j, s)] : ! d [Cl(j, d)] : ! t [Sl2(k, t)] : ! u [Rw(t, u)] : ! e [Cl(t, e)] : ! q [Sl3(k, q)] : ! w [Rw(q, w)] : ! f [Cl(q, f)] : ~x(r, c, v1) | ~x(s, d, v2) | ~x(u, e, v3) | ~x(w, f, v4).
    ! k [Ar5(k)] : ! v1 [Val(v1)] : ! v2 [Val(v2)] : ! v3 [Val(v3)] : ! v4 [Val(v4)] : ! v5 [Val(v5) & ~A5(k, v1, v2, v3, v4, v5)] : ! i [Sl0(k, i)] : ! r [Rw(i, r)] : ! c [Cl(i, c)] : ! j [Sl1(k, j)] : ! s [Rw(j, s)] : ! d [Cl(j, d)] : ! t [Sl2(k, t)] : ! u [Rw(t, u)] : ! e [Cl(t, e)] : ! q [Sl3(k, q)] : ! w [Rw(q, w)] : ! f [Cl(q, f)] : ! y [Sl4(k, y)] : ! z [Rw(y, z)] : ! g [Cl(y, g)] : ~x(r, c, v1) | ~x(s, d, v2) | ~x(u, e, v3) | ~x(w, f, v4) | ~x(z, g, v5).
}
"""


def _is_cell(node):
    return (isinstance(node, list) and len(node) == 2
            and all(isinstance(v, int) and not isinstance(v, bool) for v in node))


def _collect(node, cells, ints):
    if _is_cell(node):
        cells.append(node)
    elif isinstance(node, int) and not isinstance(node, bool):
        ints.append(node)
    elif isinstance(node, list):
        for child in node:
            _collect(child, cells, ints)


def _find_cages(node, found):
    if not isinstance(node, list) or _is_cell(node):
        return
    direct_int = any(isinstance(c, int) and not isinstance(c, bool) for c in node)
    direct_cell = any(_is_cell(c) for c in node)
    if direct_int or direct_cell:
        cells, ints = [], []
        _collect(node, cells, ints)
        found.append((cells, ints))
        return
    for child in node:
        _find_cages(child, found)


def _parse_cages(problem):
    found = []
    _find_cages(problem, found)
    cages = []
    for cells, ints in found:
        if len(ints) != 1 or not cells or len(cells) > 5:
            raise ValueError("cannot read cage: %r %r" % (cells, ints))
        cages.append((ints[0], [(r - 1, c - 1) for r, c in cells]))
    return cages


def _allowed(n, result, size):
    from itertools import product
    out = []
    for vals in product(range(1, n + 1), repeat=size):
        if size == 1:
            ok = vals[0] == result
        elif size == 2:
            a, b = vals
            hi, lo = max(a, b), min(a, b)
            ok = (a + b == result or hi - lo == result or a * b == result
                  or (hi % lo == 0 and hi // lo == result))
        else:
            prod = 1
            for v in vals:
                prod *= v
            ok = sum(vals) == result or prod == result
        if ok:
            out.append(vals)
    return out


def structure(instance):
    n = instance["n"]
    cages = _parse_cages(instance["problem"])
    cell_id = lambda r, c: r * n + c
    rel = {name: [] for name in ["Row", "Col", "Val", "Cell", "Rw", "Cl", "Ar1", "Ar2", "Ar3", "Ar4", "Ar5",
                                 "Sl0", "Sl1", "Sl2", "Sl3", "Sl4", "A1", "A2", "A3", "A4", "A5"]}
    rel["Row"] = list(range(n))
    rel["Col"] = list(range(n))
    rel["Val"] = list(range(1, n + 1))
    rel["Cell"] = list(range(n * n))
    for r in range(n):
        for c in range(n):
            rel["Rw"].append((cell_id(r, c), r))
            rel["Cl"].append((cell_id(r, c), c))
    for k, (result, cells) in enumerate(cages):
        size = len(cells)
        rel["Ar%d" % size].append(k)
        for slot, (r, c) in enumerate(cells):
            rel["Sl%d" % slot].append((k, cell_id(r, c)))
        for vals in _allowed(n, result, size):
            rel["A%d" % size].append((k,) + vals)
    return rel
