# autoref: a FOX model for GroundFOX from DCP Rosetta.
#
# Given an integer n > 0 and an integer m >= 0, find a non-empty finite series S=(s0, s1, ...,
# sn, sn+1) of integers between 0 and n such that (1) there are si occurrences of i in S for
# each integer i ranging from 0 to n, and (2) sn+1=m.
#
# Print the series S (s).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py autoref.json --check

# autoref: a FOX model for GroundFOX from DCP Rosetta.
#
# Given n > 0 and m >= 0, find a series S = (s0, ..., s_{n+1}) of integers in 0..n such that
# value i occurs exactly s_i times in S for each i in 0..n, and s_{n+1} = m.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Pq/1 Val/1 Nx/2 Ns/2 Zr/1 Ls/1 Fx/2 Hs/1 Hp/1 }
outvocabulary { s/2 Cn/3 }
theory {
    ! j [Pq(j)] : ? k [Val(k)] : s(j, k).
    ! j [Pq(j)] : ! k [Val(k)] : ! k2 [Val(k2) & ~(k = k2)] : ~s(j, k) | ~s(j, k2).
    ! z [Zr(z)] : ! i [Val(i)] : Cn(z, i, z).
    ! z [Zr(z)] : ! i [Val(i)] : ! k [Val(k) & ~Zr(k)] : ~Cn(z, i, k).
    ! j [Pq(j)] : ! j2 [Nx(j, j2)] : ! i [Val(i)] : ! k [Val(k) & Hs(k)] : ? k2 [Ns(k, k2)] : Cn(j2, i, k2) | ~Cn(j, i, k) | ~s(j, i).
    ! j [Pq(j)] : ! j2 [Nx(j, j2)] : ! i [Val(i)] : ! k [Val(k) & ~Hs(k)] : ~Cn(j, i, k) | ~s(j, i).
    ! j [Pq(j)] : ! j2 [Nx(j, j2)] : ! i [Val(i)] : ! k [Val(k)] : ~Cn(j, i, k) | s(j, i) | Cn(j2, i, k).
    ! j [Pq(j)] : ! j2 [Nx(j, j2)] : ! i [Val(i)] : ! k [Val(k) & Hp(k)] : ? k0 [Ns(k0, k)] : Cn(j, i, k0) | ~Cn(j2, i, k) | ~s(j, i).
    ! j [Pq(j)] : ! j2 [Nx(j, j2)] : ! i [Val(i)] : ! k [Val(k) & ~Hp(k)] : ~Cn(j2, i, k) | ~s(j, i).
    ! j [Pq(j)] : ! j2 [Nx(j, j2)] : ! i [Val(i)] : ! k [Val(k)] : ~Cn(j2, i, k) | s(j, i) | Cn(j, i, k).
    ! l [Ls(l)] : ! i [Val(i)] : ! k [Val(k)] : ~s(i, k) | Cn(l, i, k).
    ! p : ! v [Fx(p, v)] : s(p, v).
}
"""


def structure(instance):
    n = instance["n"]
    m = instance["m"]
    top = max(n + 2, m)
    return {
        "domain": range(top + 1),
        "Pq": range(n + 2),
        "Val": range(n + 1),
        "Nx": [(j, j + 1) for j in range(n + 2)],
        "Ns": [(k, k + 1) for k in range(n)],
        "Zr": [0],
        "Ls": [n + 2],
        "Fx": [(n + 1, m)],
        "Hs": list(range(n)),
        "Hp": list(range(1, n + 1)),
    }
