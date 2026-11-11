% session1_money_change: a MiniZinc model from DCP Rosetta.
%
% Alice has to give Bob some change. She has different types of coins of different values and she has a certain number of
% coins of each value available. How can the change be composed with the available coins minimizing the number of coins used?
%
% Save this file as model.mzn. Download `session1_money_change.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session1_money_change.json
%   minizinc model.mzn session1_money_change_1.json

int: amount;                                         % the amount of change to give
array[int] of int: types_of_coins;                   % types_of_coins[i]: the value of a coin of type i
array[int] of int: available_coins;                  % available_coins[i]: the number of coins of type i available

set of int: Types = index_set(types_of_coins);       % one index per type of coin

array[Types] of var int: coin_counts;                % coin_counts[i]: the number of coins of type i given to Bob
var int: objective = sum(i in Types)(coin_counts[i]);

% Bob is given no more coins of a type than are available
constraint forall(i in Types)(coin_counts[i] >= 0 /\ coin_counts[i] <= available_coins[i]);

% the coins given to Bob add up to the amount of change
constraint sum(i in Types)(types_of_coins[i] * coin_counts[i]) = amount;

solve minimize objective;
output ["{\"coin_counts\": ", showJSON(coin_counts), "}"];
