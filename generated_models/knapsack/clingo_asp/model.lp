% knapsack: a clingo model from DCP Rosetta.
%
% A hiker is planning a trip and needs to decide which items to take in their backpack. Each item has a
% certain value and weight, and the hiker wants to maximize the total value of the items in the backpack
% without exceeding the weight capacity of the backpack.
%
% Save this file as model.lp. Download `knapsack.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py knapsack.json
%   python -m clingo model.lp knapsack_1.lp
%
% Input: capacity(C) holds the weight capacity C of the backpack; values(I, V) and weights(I, W) hold the
% value V and the weight W of item I (indices are 0-based, as in the data).

% the items are those that have a value
item(I) :- values(I, _).

% each item is either taken (x(I,1)) or not (x(I,0))
{ x(I, 1) } :- item(I).
x(I, 0) :- item(I), not x(I, 1).

% the items taken weigh no more than the capacity of the backpack
:- capacity(C), #sum { W, I : x(I, 1), weights(I, W) } > C.

% maximize the total value of the items taken
#maximize { V, I : x(I, 1), values(I, V) }.

#show x/2.
