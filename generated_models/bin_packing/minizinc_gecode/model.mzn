% bin_packing: a MiniZinc model from DCP Rosetta.
%
% Given several items of specific weights and a number of bins of a fixed capacity, assign each
% item to a bin so that the total weight of the items in each bin does not exceed the capacity.
%
% Save this file as model.mzn. Download `bin_packing.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py bin_packing.json
%   minizinc model.mzn bin_packing_1.json

include "globals.mzn";

int: capacity;                          % the total weight each bin can hold
int: num_bins;                          % the number of bins available
array[int] of int: weights;             % weights[i]: the weight of item i

set of int: Items = index_set(weights); % one index per item
set of int: Bins = 0..num_bins-1;       % bins are numbered from 0

% bins[i]: the bin item i is assigned to
array[Items] of var Bins: bins;

% the total weight of the items in each bin does not exceed the capacity
constraint bin_packing(capacity, bins, weights);

solve satisfy;

output ["{\"bins\": ", showJSON(bins), "}"];
