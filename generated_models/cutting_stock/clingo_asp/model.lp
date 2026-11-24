% cutting_stock: a clingo model from DCP Rosetta.
%
% This is a cutting stock problem. Raw rolls of a fixed width are cut with a given set of cutting patterns,
% each pattern yielding a fixed number of pieces of each width, and orders[i] pieces of width widths[i] are
% needed. Find how many rolls to cut with each pattern so that, for every width, at least the ordered number
% of pieces is produced, with as few raw rolls cut as possible.
%
% Save this file as model.lp. Download `cutting_stock.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py cutting_stock.json
%   python -m clingo model.lp cutting_stock_1.lp

% Input: num_patterns(P) holds the number P of cutting patterns; orders(W, O) holds the number O of pieces
% of width index W that are ordered; num_rolls_width(J, W, C) holds the number C of pieces of width index W
% that pattern J yields (indices are 0-based, as in the data).

pattern(0..P-1) :- num_patterns(P).

% the number of times a pattern is used is at most the largest order: with more uses, one use less still
% gives every width that the pattern yields at least the largest order, so it is still a cover and costs
% a roll less
max_order(M) :- M = #max { O : orders(_,O) }.
multiplicity(0..M) :- max_order(M).

% each pattern J is used V times, for exactly one V
1 { patterns_used(J,V) : multiplicity(V) } 1 :- pattern(J).

% for each width, the pieces cut over all patterns are at least the ordered number
:- orders(W,O), #sum { V*C,J : patterns_used(J,V), num_rolls_width(J,W,C) } < O.

% min_rolls_cut: the total number of raw rolls cut, to be minimised
min_rolls_cut(T) :- T = #sum { V,J : patterns_used(J,V) }.
#minimize { V,J : patterns_used(J,V) }.

#show patterns_used/2.
#show min_rolls_cut/1.
