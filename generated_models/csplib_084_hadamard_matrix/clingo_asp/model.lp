% csplib_084_hadamard_matrix: a clingo model from DCP Rosetta.
%
% For every odd positive integer l, with m = (l - 1) / 2, find two sequences a and b of l entries, each -1 or +1,
% such that the entries of a sum to 1 and the entries of b sum to 1, and such that for every shift s = 1..m the
% periodic autocorrelations of a and b add up to -2: PAF(a, s) + PAF(b, s) = -2, where PAF(x, s) is the sum over i
% of x_i times x_(i+s), with i+s taken mod l.
%
% Save this file as model.lp. Download `csplib_084_hadamard_matrix.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_084_hadamard_matrix.json
%   python -m clingo model.lp csplib_084_hadamard_matrix_1.lp

% Input: l(L) holds the length L of the sequences (an odd positive integer).

% the positions of the sequences are 0..L-1, the shifts are 1..m, and the entries are -1 or +1
index(0..L-1) :- l(L).
shift(1..(L-1)/2) :- l(L).
sign(-1;1).

% each entry of a, and each entry of b, is -1 or +1
1 { a(I,V) : sign(V) } 1 :- index(I).
1 { b(I,V) : sign(V) } 1 :- index(I).

% the entries of a sum to 1
:- #sum { V,I : a(I,V) } != 1.

% the entries of b sum to 1
:- #sum { V,I : b(I,V) } != 1.

% PAF(a, s): the sum over i of a_i times a_((i+s) mod l), for each shift s
paf_a(S,P) :- shift(S), l(L), P = #sum { VA*VB,I : a(I,VA), a((I+S) \ L,VB) }.

% PAF(b, s): the sum over i of b_i times b_((i+s) mod l), for each shift s
paf_b(S,P) :- shift(S), l(L), P = #sum { VA*VB,I : b(I,VA), b((I+S) \ L,VB) }.

% PAF(a, s) + PAF(b, s) = -2 for every shift s
:- paf_a(S,P), paf_b(S,Q), P + Q != -2.

#show a/2.
#show b/2.
