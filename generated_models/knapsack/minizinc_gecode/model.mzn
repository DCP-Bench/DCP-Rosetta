% knapsack: a MiniZinc model from DCP Rosetta.
%
% A hiker is planning a trip and must decide which items to put in the backpack. Each item has a value
% and a weight, and the hiker wants to maximize the total value of the items in the backpack without
% exceeding the weight capacity of the backpack.
%
% Save this file as model.mzn. Download `knapsack.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py knapsack.json
%   minizinc model.mzn knapsack_1.json

int: capacity;                                   % the weight capacity of the backpack
array[int] of int: values;                       % values[i]: value of item i
array[int] of int: weights;                      % weights[i]: weight of item i
set of int: Items = index_set(values);           % the items

array[Items] of var bool: x;                     % x[i]: item i is taken
var int: objective = sum(i in Items)(values[i] * bool2int(x[i]));

% the items taken weigh no more than the capacity of the backpack
constraint sum(i in Items)(weights[i] * bool2int(x[i])) <= capacity;

solve maximize objective;
output ["{\"x\": ", showJSON(x), "}"];
