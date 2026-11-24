% session2_subset_sum: a clingo model from DCP Rosetta.
%
% A bank van had several bags of coins, each containing a number of coins from a given list (there are multiple bags of the same kind). While the van was parked on the street, thieves stole some bags. A total of a given number of coins were lost. It is required to find how many bags were stolen for each type of coin bag.
%
% Save this file as model.lp. Download `session2_subset_sum.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session2_subset_sum.json
%   python -m clingo model.lp session2_subset_sum_1.lp
%
% Input: coin_numbers(I, C) holds the number C of coins in a bag of type I; total_coins_lost(T) holds the
% total number T of coins lost (indices are 0-based, as in the data).

bag_type(I) :- coin_numbers(I, _).

% the candidate numbers of bags stolen of one type run from 0 up to the total number of coins lost
count_value(0..T) :- total_coins_lost(T).

% for each type, a number of bags stolen is chosen
{ bags(I, N) : count_value(N) } = 1 :- bag_type(I).

% the bags stolen together contain exactly the total number of coins lost
:- total_coins_lost(T), #sum { N * C, I : bags(I, N), coin_numbers(I, C) } != T.

#show bags/2.
