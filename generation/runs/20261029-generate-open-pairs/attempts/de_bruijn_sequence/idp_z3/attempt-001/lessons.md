Blind model. Read the earlier idp_z3 attempts' evaluation details (20261020-idp-structure,
attempts 001-003): `base() ^ n()` does not type, and `Pos_size() = pw(n())` with pw defined by
recursion does not fold. Here the length base^n is folded as a count:
`#{ d1..d6 in Range_base: slots beyond n pinned to 1 }`, which is exact for n =< 6 (the model
states n =< 6, so a larger order is refused rather than answered wrongly). The window index
p = i + j - 1 (or minus base^n past the end) is quantified over p in Pos, which keeps every
de_bruijn(p) well-defined. A Horner code `code(i, j-1) * base()` timed out on B(2,4):
base() is a z3 constant there, so the product is nonlinear; pairwise "windows differ in some
symbol" solves every instance in 1-3 s.
