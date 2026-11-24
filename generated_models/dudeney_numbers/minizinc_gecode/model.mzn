% dudeney_numbers: a MiniZinc model from DCP Rosetta.
%
% A Dudeney Number is a positive integer that is a perfect cube such that the sum of its digits is
% equal to the cube root of the number.
%
% Save this file as model.mzn. Download `dudeney_numbers.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py dudeney_numbers.json
%   minizinc model.mzn dudeney_numbers_1.json

int: n;                                      % the maximum number of digits

set of int: Positions = 1..n;                % digit positions, units first
array[Positions] of var 0..9: digits;        % digits[p]: the digit at position p

var int: number = sum(p in Positions)(digits[p] * pow(10, p - 1));
var 2..9*n: cube_root;                       % the cube root of number, at most 9n since its digits sum to it

% the number is a perfect cube
constraint number = cube_root * cube_root * cube_root;
% the sum of the digits of the number is equal to its cube root
constraint sum(p in Positions)(digits[p]) = cube_root;
% the number is larger than 1
constraint number > 1;
% the number has at most n digits
constraint number < pow(10, n);

solve satisfy;
output ["{\"number\": ", showJSON(number), "}"];
