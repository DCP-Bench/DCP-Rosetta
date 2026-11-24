% cutting_stock: a MiniZinc model from DCP Rosetta.
%
% Cutting stock: raw rolls of a fixed width are cut into pieces of several smaller widths. Each cutting
% pattern i yields num_rolls_width[i, j] pieces of width j from one roll, and orders[j] pieces of each
% width j are needed. Choose how many rolls to cut with each pattern so that at least the ordered number
% of pieces of each width is produced, using as few raw rolls as possible.
%
% Save this file as model.mzn. Download `cutting_stock.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py cutting_stock.json
%   minizinc model.mzn cutting_stock_1.json

array[int,int] of int: num_rolls_width;          % num_rolls_width[i,j]: pieces of width j from one roll cut with pattern i
array[int] of int: orders;                       % orders[j]: pieces of width j that are needed

set of int: Patterns = index_set_1of2(num_rolls_width);  % the cutting patterns
set of int: Widths = index_set(orders);          % the piece widths

% patterns_used[i]: the number of rolls cut with pattern i (at most sum(orders): more rolls than ordered pieces is never needed in an optimum)
array[Patterns] of var 0..sum(orders): patterns_used;
var int: objective = sum(i in Patterns)(patterns_used[i]);

% at least the ordered number of pieces of each width is produced
constraint forall(j in Widths)(
    sum(i in Patterns)(num_rolls_width[i, j] * patterns_used[i]) >= orders[j]
);

solve minimize objective;
output ["{\"patterns_used\": ", showJSON(patterns_used), ", \"min_rolls_cut\": ", show(objective), "}"];
