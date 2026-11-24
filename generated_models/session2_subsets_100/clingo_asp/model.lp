% session2_subsets_100: a clingo model from DCP Rosetta.
%
% From a set A of integers you can always find two disjoint non-empty subsets, S and T, such that the sum of the elements in S equals the sum of the elements in T. S union T does not need to be all the elements of A. Find sets S and T for the given set A.
%
% Save this file as model.lp. Download `session2_subsets_100.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session2_subsets_100.json
%   python -m clingo model.lp session2_subsets_100_1.lp
%
% Input: a(I, V) holds the integer V of element I of the set A (indices are 0-based, as in the data).

item(I) :- a(I, _).

% each element may be in S, and each may be in T
{ s_member(I) } :- item(I).
{ t_member(I) } :- item(I).

% S and T are disjoint
:- s_member(I), t_member(I).

% S and T are non-empty
:- #count { I : s_member(I) } = 0.
:- #count { I : t_member(I) } = 0.

% the sum of the elements in S equals the sum of the elements in T
sum_S(S) :- S = #sum { V, I : s_member(I), a(I, V) }.
sum_T(T) :- T = #sum { V, I : t_member(I), a(I, V) }.
:- sum_S(S), sum_T(T), S != T.

% the output: for each element, true when it is in the subset and false otherwise
in_S(I, true)  :- s_member(I).
in_S(I, false) :- item(I), not s_member(I).
in_T(I, true)  :- t_member(I).
in_T(I, false) :- item(I), not t_member(I).

#show in_S/2.
#show in_T/2.
