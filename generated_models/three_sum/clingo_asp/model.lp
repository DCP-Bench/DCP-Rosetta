% three_sum: a clingo model from DCP Rosetta.
%
% Given a collection of integers, find exactly `m` elements that sum to zero.
%
% Save this file as model.lp. Download `three_sum.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py three_sum.json
%   python -m clingo model.lp three_sum_1.lp
%
% Input: m(M) holds the number M of elements to find; nums(I, V) holds the integer V at position I (0-based).

item(I) :- nums(I, _).

% each element is either selected (indices(I,1)) or not (indices(I,0))
{ indices(I, 1) } :- item(I).
indices(I, 0) :- item(I), not indices(I, 1).

% exactly m elements are selected
:- m(M), #count { I : indices(I, 1) } != M.

% the selected elements sum to zero
:- #sum { V, I : indices(I, 1), nums(I, V) } != 0.

#show indices/2.
