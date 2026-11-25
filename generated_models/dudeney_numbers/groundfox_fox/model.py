# dudeney_numbers: a FOX model for GroundFOX from DCP Rosetta.
#
# A Dudeney Number is a positive integer that is a perfect cube such that the sum of its
# digits is equal to the cube root of the number.
#
# Print such a number (number) that is also larger than 1 and has at most n digits.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py dudeney_numbers.json --check

# dudeney_numbers: a FOX model for GroundFOX from DCP Rosetta.
#
# A Dudeney number is a perfect cube k^3 > 1 with at most n digits whose digit sum equals k.
# The root k is chosen (root/1); the digits of the number are forced to the digits of k^3
# (precomputed from the instance size), and the digit sum is checked by a partial-sum state
# chain over the digit positions. The root is at most the largest possible digit sum (9n),
# so that every candidate sum is a state of the chain. Output number is k^3.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Rt/1 Cube/2 Val/1 Dig/1 Pos/1 Lvl/1 Next/2 Last/1 Sum/1 Add/3 DigOf/3 Init/1 }
outvocabulary { number/1 root/1 dg/2 st/2 }
theory {
    ? c [Val(c)] : number(c).
    ! c [Val(c)] : ! d [Val(d) & c ~= d] : ~number(c) | ~number(d).
    ! c [Val(c)] : ! k [Cube(k,c)] : ~number(c) | root(k).
    ? k [Rt(k)] : root(k).
    ! k [Rt(k)] : ! l [Rt(l) & k ~= l] : ~root(k) | ~root(l).
    ! k [Rt(k)] : ! c [Cube(k,c)] : ~root(k) | number(c).
    ! i [Pos(i)] : ? v [Dig(v)] : dg(i,v).
    ! i [Pos(i)] : ! v [Dig(v)] : ! w [Dig(w) & v ~= w] : ~dg(i,v) | ~dg(i,w).
    ! k [Rt(k)] : ! i [Pos(i)] : ! v [Dig(v) & ~DigOf(k,i,v)] : ~root(k) | ~dg(i,v).
    ! z [Init(z)] : st(z,z).
    ! i [Pos(i)] : ! j [Next(i,j)] : ! s [Sum(s)] : ! v [Dig(v)] : ! t [Sum(t) & Add(s,v,t)] : ~st(i,s) | ~dg(i,v) | st(j,t).
    ! j [Lvl(j)] : ? s [Sum(s)] : st(j,s).
    ! j [Lvl(j)] : ! s [Sum(s)] : ! t [Sum(t) & s ~= t] : ~st(j,s) | ~st(j,t).
    ! k [Rt(k)] : ! l [Last(l)] : ~root(k) | st(l,k).
}
"""


def structure(instance):
    n = instance["n"]
    lim = 10 ** n
    max_sum = 9 * n
    # Candidate roots: 2 <= k <= 9n (a digit sum never exceeds 9n) with k^3 having at most n digits.
    roots = [k for k in range(2, max_sum + 1) if k ** 3 < lim]
    cubes = [k ** 3 for k in roots]
    cube = [(k, k ** 3) for k in roots]
    digof = [(k, i, (k ** 3 // 10 ** i) % 10) for k in roots for i in range(n)]
    add = [(s, v, s + v) for s in range(max_sum + 1) for v in range(10) if s + v <= max_sum]
    dom = set(range(max(max_sum, n) + 1)) | set(cubes)
    return {
        "domain": sorted(dom),
        "Rt": roots,
        "Cube": cube,
        "Val": cubes,
        "Dig": list(range(10)),
        "Pos": list(range(n)),
        "Lvl": list(range(n + 1)),
        "Next": [(i, i + 1) for i in range(n)],
        "Last": [n],
        "Sum": list(range(max_sum + 1)),
        "Add": add,
        "DigOf": digof,
        "Init": [0],
    }
