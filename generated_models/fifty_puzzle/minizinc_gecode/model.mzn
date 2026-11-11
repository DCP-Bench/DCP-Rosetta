% fifty_puzzle: a MiniZinc model from DCP Rosetta.
%
% A side show is described as follows: "There were a number of little dummies which you were to knock
% over with baseballs. The man said: 'Take as many throws as you like at a cent apiece and stand as
% close as you please. Add up the numbers on all the men that you knock down and when the sum amounts
% to exactly a given target sum, neither more nor less you get a genuine prize.'"
% The numbers on the dummies are given as a list of integers.
%
% Save this file as model.mzn. Download `fifty_puzzle.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py fifty_puzzle.json
%   minizinc model.mzn fifty_puzzle_1.json

array[int] of int: values;                   % values[i]: the number on dummy i
int: target_sum;                             % the sum that must be knocked down exactly
set of int: Dummies = index_set(values);     % one index per dummy

% dummies[i]: dummy i is knocked over
array[Dummies] of var bool: dummies;

% the knocked-over dummies add up to exactly the target sum
constraint sum(i in Dummies)(values[i] * bool2int(dummies[i])) = target_sum;

solve satisfy;
output ["{\"dummies\": ", showJSON(dummies), "}"];
