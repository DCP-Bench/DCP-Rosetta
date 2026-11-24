% csplib_019_magic_squares_and_sequences: a MiniZinc model from DCP Rosetta.
%
% A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1} between 0 and n-1, such that for
% all i in 0 to n-1, the number i occurs exactly x_i times in the sequence. For example, 6, 2, 1, 0, 0, 0, 1, 0, 0, 0
% is a magic sequence since 0 occurs 6 times in it, 1 occurs twice, etc.
%
% Save this file as model.mzn. Download `csplib_019_magic_squares_and_sequences.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_019_magic_squares_and_sequences.json
%   minizinc model.mzn csplib_019_magic_squares_and_sequences_1.json

int: n;                                      % the length of the sequence
set of int: Positions = 1..n;                % the positions of the sequence
set of int: Values = 0..n - 1;               % the values the sequence holds

array[Positions] of var Values: x;           % x[i]: the entry at position i

% the value i - 1 occurs exactly x[i] times in the sequence
constraint forall(i in Positions)(count(x, i - 1) = x[i]);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
