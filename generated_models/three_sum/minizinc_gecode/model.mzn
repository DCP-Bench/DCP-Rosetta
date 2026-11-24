% three_sum: a MiniZinc model from DCP Rosetta.
%
% Given a collection of integers, find exactly `m` elements that sum to zero.
%
% Save this file as model.mzn. Download `three_sum.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py three_sum.json
%   minizinc model.mzn three_sum_1.json

array[int] of int: nums;                 % the collection of integers
int: m;                                  % how many elements to select
set of int: Items = index_set(nums);     % one index per integer

array[Items] of var bool: indices;       % indices[i]: element i is selected

% the selected elements sum to zero
constraint sum(i in Items)(nums[i] * bool2int(indices[i])) = 0;

% exactly m elements are selected
constraint sum(i in Items)(bool2int(indices[i])) = m;

solve satisfy;
output ["{\"indices\": ", showJSON(indices), "}"];
