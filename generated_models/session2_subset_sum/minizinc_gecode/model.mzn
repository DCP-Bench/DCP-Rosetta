% session2_subset_sum: a MiniZinc model from DCP Rosetta.
%
% A bank van had several bags of coins, each containing a number of coins from a given list (there are
% multiple bags of the same kind). While the van was parked on the street, thieves stole some bags. A total
% of a given number of coins were lost. Find how many bags were stolen for each type of coin bag.
%
% Save this file as model.mzn. Download `session2_subset_sum.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session2_subset_sum.json
%   minizinc model.mzn session2_subset_sum_1.json

include "globals.mzn";

int: total_coins_lost;                        % the total number of coins lost
array[int] of int: coin_numbers;              % coin_numbers[k]: number of coins in a bag of type k

set of int: Kinds = index_set(coin_numbers);  % one index per type of coin bag

array[Kinds] of var 0..total_coins_lost: bags;  % bags[k]: number of stolen bags of type k

% the stolen bags contain exactly the total number of coins lost
constraint sum(k in Kinds)(coin_numbers[k] * bags[k]) = total_coins_lost;

solve satisfy;
output ["{\"bags\": ", showJSON(bags), "}"];
