% added_corners: a MiniZinc model from DCP Rosetta.
%
% Enter the digits 1 through 8 into the eight positions around the edge of a 3 by 3 grid whose centre
% is empty, using each digit exactly once. The corners are circles and the middles of the sides are
% squares. The number in each square must equal the sum of the numbers in the two circles adjoining it.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: n = 8;                                  % the digits, one per edge position
set of int: Digits = 1..n;

% positions read like a book, left to right and top to bottom:
%   1 2 3
%   4   5
%   6 7 8
% the corners 1, 3, 6 and 8 are circles, the side middles 2, 4, 5 and 7 are squares
array[1..n] of var Digits: positions;

% the digits 1 through 8 are each entered exactly once
constraint all_different(positions);

% the square at position 2 is the sum of the circles at positions 1 and 3
constraint positions[2] = positions[1] + positions[3];

% the square at position 4 is the sum of the circles at positions 1 and 6
constraint positions[4] = positions[1] + positions[6];

% the square at position 5 is the sum of the circles at positions 3 and 8
constraint positions[5] = positions[3] + positions[8];

% the square at position 7 is the sum of the circles at positions 6 and 8
constraint positions[7] = positions[6] + positions[8];

solve satisfy;

output ["{\"positions\": ", showJSON(positions), "}"];
