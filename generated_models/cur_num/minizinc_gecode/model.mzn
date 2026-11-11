% cur_num: a MiniZinc model from DCP Rosetta.
%
% The number 48 has this peculiarity, that if you add 1 to it the result is a square number, and if you
% add 1 to its half, you also get a square number. Find another number with this peculiarity between 1
% and 10000.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

% the bounds of the search range, and the number that is excluded
int: lo = 1;
int: hi = 10000;
int: known = 48;

var lo..hi: peculiar;                            % the number with the peculiarity
var 0..ceil(sqrt(int2float(hi + 1))): root_plus_one;  % root_plus_one^2 = peculiar + 1, so at most sqrt(hi + 1)
var 0..ceil(sqrt(int2float(hi div 2 + 1))): root_half_plus_one;  % root_half_plus_one^2 = peculiar / 2 + 1, so at most sqrt(hi / 2 + 1)

% the number is another one than 48
constraint peculiar != known;

% its half is a whole number
constraint peculiar mod 2 = 0;

% adding 1 to the number gives a square number
constraint root_plus_one * root_plus_one = peculiar + 1;

% adding 1 to its half gives a square number
constraint root_half_plus_one * root_half_plus_one = peculiar div 2 + 1;

solve satisfy;
output ["{\"peculiar\": ", showJSON(peculiar), "}"];
