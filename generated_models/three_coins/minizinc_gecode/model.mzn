% three_coins: a MiniZinc model from DCP Rosetta.
%
% Three coins lie on a table in the order tails, heads, tails. In precisely three moves make them
% face either all heads or all tails. Each move consists of choosing one coin and flipping it over.
%
% Save this file as model.mzn. Download `three_coins.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py three_coins.json
%   minizinc model.mzn three_coins_1.json

int: num_moves;                                % the number of moves
array[int] of int: init;                       % init[j]: the starting face of coin j, 1 for tails, 0 for heads
set of int: Coins = index_set(init);           % the coins
set of int: Steps = 0..num_moves;              % the configurations: the initial one, then one after each move

% x[m,j]: coin j shows tails (true) or heads (false) in configuration m
array[Steps, Coins] of var bool: x;

% the initial configuration is the given one
constraint forall(j in Coins)(x[0,j] = (init[j] = 1));

% each move flips exactly one coin
constraint forall(m in 1..num_moves)(sum(j in Coins)(bool2int(x[m,j] != x[m-1,j])) = 1);

% at the end all coins face the same way, all heads or all tails
constraint forall(j in Coins)(x[num_moves,j] = x[num_moves,min(Coins)]);

solve satisfy;
output ["{\"steps\": ", showJSON(x), "}"];
