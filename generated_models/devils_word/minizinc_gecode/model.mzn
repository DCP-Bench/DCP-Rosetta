% devils_word: a MiniZinc model from DCP Rosetta.
%
% Given an array of integers, insert a '+' or a '-' operator before each integer so that summing them up
% gives a given total.
%
% Save this file as model.mzn. Download `devils_word.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py devils_word.json
%   minizinc model.mzn devils_word_1.json

array[int] of int: arr;                          % the integers
int: total;                                      % the sum the signed integers must give

set of int: Pos = index_set(arr);                % one index per integer
int: abs_sum = sum(i in Pos)(abs(arr[i]));       % the largest possible absolute value of the sum

% sign[i]: the operator before integer i, + (1) or - (-1)
array[Pos] of var {-1, 1}: sign;

% result[i]: integer i with its sign in front
array[Pos] of var -abs_sum..abs_sum: result;

% each integer carries the sign chosen before it
constraint forall(i in Pos)(result[i] = sign[i] * arr[i]);

% the signed integers sum to the total
constraint sum(i in Pos)(result[i]) = total;

solve satisfy;
output ["{\"result\": ", showJSON(result), "}"];
