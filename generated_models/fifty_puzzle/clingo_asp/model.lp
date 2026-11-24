% fifty_puzzle: a clingo model from DCP Rosetta.
%
% There are a number of little dummies to knock over with baseballs, and each dummy has a number on it. Each dummy may be knocked over at most once, and you want the numbers on the dummies you knock over to add up to exactly a given target sum, neither more nor less.
%
% Save this file as model.lp. Download `fifty_puzzle.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py fifty_puzzle.json
%   python -m clingo model.lp fifty_puzzle_1.lp

% Input: values(I, V) holds the number V on dummy I (indices 0-based); target_sum(T) holds the target sum T.

% the dummies are those that have a number
dummy(I) :- values(I, _).

% each dummy is knocked over (knocked(I)) or not
{ knocked(I) : dummy(I) }.

% the numbers on the dummies knocked over add up to exactly the target sum
:- target_sum(T), #sum { V, I : knocked(I), values(I, V) } != T.

% the output: each dummy as true (knocked over) or false
dummies(I, true) :- knocked(I).
dummies(I, false) :- dummy(I), not knocked(I).

#show dummies/2.
