% csplib_006_golomb_rulers: a clingo model from DCP Rosetta.
%
% A Golomb ruler is a set of m integers 0 = a_1 < a_2 < ... < a_m such that the m(m-1)/2 differences
% a_j - a_i, 1 <= i < j <= m, are distinct. Such a ruler contains m marks and has length a_m. Find
% optimal rulers, that is rulers of minimum length.
%
% Save this file as model.lp. Download `csplib_006_golomb_rulers.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_006_golomb_rulers.json
%   python -m clingo model.lp csplib_006_golomb_rulers_1.lp
%
% Input: size(S) holds the number S of marks (indices are 0-based, as in the data).

% the positions a mark may take: 0 up to size * size. This bound is not part of the problem: it is an assumed
% upper limit, since optimal Golomb rulers are known to be shorter than size * size, so no optimal ruler is excluded
position(0..M) :- size(S), M = S * S.

% mark(P): there is a mark at position P; the first mark is at 0
mark(0).
{ mark(P) : position(P), P > 0 }.

% the ruler has exactly size marks
:- size(S), #count { P : mark(P) } != S.

% the distances that can occur between two marks
distance(D) :- position(D), D > 0.

% difference(D,P): there are marks at P and at P + D
difference(D,P) :- distance(D), mark(P), mark(P + D).

% Golomb condition: every distance is the difference of at most one pair of marks
:- distance(D), #count { P : difference(D,P) } > 1.

% Implied by the Golomb condition, to prune early: K + 1 marks have K distinct gaps between
% neighbouring marks, which add up to at least 1 + 2 + ... + K = K * (K + 1) / 2. So any K * (K + 1) / 2
% consecutive positions hold at most K marks.
:- size(S), K = 1..S-1, position(P), #count { Q : mark(Q), P <= Q, Q < P + K * (K + 1) / 2 } > K.

% marks(I,P): the I-th mark, counted from 0 in increasing order, is at position P
marks(I,P) :- mark(P), I = #count { Q : mark(Q), Q < P }.

% the length of the ruler is the position of its last mark
length(L) :- L = #max { P : mark(P) }.

% the length of the ruler is as small as possible
#minimize { L : length(L) }.

#show marks/2.
#show length/1.
