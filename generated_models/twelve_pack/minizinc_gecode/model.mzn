% twelve_pack: a MiniZinc model from DCP Rosetta.
%
% Given a target number of items, find the combination of packs of different sizes whose total number
% of items is at least the target and as close to it as possible.
%
% Save this file as model.mzn. Download `twelve_pack.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py twelve_pack.json
%   minizinc model.mzn twelve_pack_1.json

include "globals.mzn";

int: target;                             % the target number of items
array[int] of int: packs;                % packs[i]: the number of items in a pack of size i
set of int: Sizes = index_set(packs);    % one index per pack size

% counts[i]: how many packs of size i are bought; each pack holds at least one item, so no
% more than target packs of one size can be useful
array[Sizes] of var 0..target: counts;

var int: total = sum(i in Sizes)(counts[i] * packs[i]);  % the number of items bought

% the total number of items is at least the target
constraint total >= target;

var int: objective = total;              % the number of items bought, minimised: the least overshoot above the target

solve minimize objective;
output ["{\"counts\": ", showJSON(counts), "}"];
