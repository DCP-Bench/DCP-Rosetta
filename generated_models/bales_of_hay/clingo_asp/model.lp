% bales_of_hay: a clingo model from DCP Rosetta.
%
% You have a number of bales of hay. For some reason, instead of being weighed individually, they were weighed in all possible combinations of two. The weights of each of these combinations were written down and arranged in numerical order, without keeping track of which weight matched which pair of bales. The weights are given in a list.
%
% Save this file as model.lp. Download `bales_of_hay.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py bales_of_hay.json
%   python -m clingo model.lp bales_of_hay_1.lp

% Input: n(N) holds the number N of bales; weights(K, W) holds the weight W of the K-th pair in the list (indices are 0-based).

bale(0..N-1) :- n(N).
pair(I, J) :- bale(I), bale(J), I < J.

% the bales are integers within twice the largest weight in absolute value (a bound for the search)
bound(2 * M) :- M = #max { |W| : weights(_, W) }.
value(-B..B) :- bound(B).

% each bale has exactly one weight
1 { bales(I, V) : value(V) } 1 :- bale(I).

% the sum of the weights of each pair of bales
pairsum(I, J, S) :- pair(I, J), bales(I, A), bales(J, B), S = A + B.

% the weights of the pairs are the given weights
wval(W) :- weights(_, W).
:- pairsum(_, _, S), not wval(S).

% how often each given weight is in the list, and how often it is among the pair sums
listed(W, C) :- wval(W), C = #count { K : weights(K, W) }.
summed(W, C) :- wval(W), C = #count { I, J : pairsum(I, J, W) }.

% each given weight occurs among the pair sums as often as it is in the list
:- listed(W, C), summed(W, D), C != D.

#show bales/2.
