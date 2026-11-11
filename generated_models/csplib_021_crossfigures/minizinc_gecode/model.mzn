% csplib_021_crossfigures: a MiniZinc model from DCP Rosetta.
%
% Crossfigures are the numerical equivalent of crosswords. You have a grid and some
% clues with numerical answers to place on this grid. Clues come in several different
% forms (for example: Across 1. 25 across times two, 2. five dozen, 5. a square number,
% 10. prime, 14. 29 across times 21 down ...).
% Here is the specific problem:
% ```text
%   1  2  3  4  5  6  7  8  9
%   ---------------------------
%   1  2  _  3  X  4  _  5  6    1
%   7  _  X  8  _  _  X  9  _    2
%   _  X  10 _  X  11 12 X  _    3
%   13 14 _  _  X  15 _  16 _    4
%   X  _  X  X  X  X  X  _  X    5
%   17 _  18 19 X  20 21 _ 22    6
%   _  X  23 _  X  24 _  X  _    7
%   25 26 X  27 _  _  X  28 _    8
%   29 _  _  _  X  30 _  _  _    9
% ```
% Here are the clues:
% ```text
% Across
%   1 27 across times two
%   4 4 down plus seventy-one
%   7 18 down plus four
%   8 6 down divided by sixteen
%   9 2 down minus eighteen
%  10 Dozen in six gross
%  11 5 down minus seventy
%  13 26 down times 23 across
%  15 6 down minus 350
%  17 25 across times 23 across
%  20 A square number
%  23 A prime number
%  24 A square number
%  25 20 across divided by seventeen
%  27 6 down divided by four
%  28 Four dozen
%  29 Seven gross
%  30 22 down plus 450
% Down
%   1 1 across plus twenty-seven
%   2 Five dozen
%   3 30 across plus 888
%   4 Two times 17 across
%   5 29 across divided by twelve
%   6 28 across times 23 across
%  10 10 across plus four
%  12 Three times 24 across
%  14 13 across divided by sixteen
%  16 28 down times fifteen
%  17 13 across minus 399
%  18 29 across divided by eighteen
%  19 22 down minus ninety-four
%  20 20 across minus nine
%  21 25 across minus fifty-two
%  22 20 down times six
%  26 Five times 24 across
%  28 21 down plus twenty-seven
% ```
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

set of int: Rows = 1..9;                     % the rows of the grid
set of int: Cols = 1..9;                     % the columns of the grid

% the digit in row r and column c of the grid (0 for a cell marked X)
array[Rows, Cols] of var 0..9: M;

% the number written by a run of digits ds, most significant first
function var int: number(array[int] of var 0..9: ds) = sum(i in index_set(ds))(ds[i] * pow(10, length(ds) - i));

% the cells marked X hold 0
constraint M[1,5] = 0 /\
    M[2,3] = 0 /\
    M[2,7] = 0 /\
    M[3,2] = 0 /\
    M[3,5] = 0 /\
    M[3,8] = 0 /\
    M[4,5] = 0 /\
    M[5,1] = 0 /\
    M[5,3] = 0 /\
    M[5,4] = 0 /\
    M[5,5] = 0 /\
    M[5,6] = 0 /\
    M[5,7] = 0 /\
    M[5,9] = 0 /\
    M[6,5] = 0 /\
    M[7,2] = 0 /\
    M[7,5] = 0 /\
    M[7,8] = 0 /\
    M[8,3] = 0 /\
    M[8,7] = 0 /\
    M[9,5] = 0;

% the answer of each run of cells read across (A) or down (D), numbered as in the grid
var 0..9999: A1 = number([M[1,1], M[1,2], M[1,3], M[1,4]]);
var 0..9999: A4 = number([M[1,6], M[1,7], M[1,8], M[1,9]]);
var 0..99: A7 = number([M[2,1], M[2,2]]);
var 0..999: A8 = number([M[2,4], M[2,5], M[2,6]]);
var 0..99: A9 = number([M[2,8], M[2,9]]);
var 0..99: A10 = number([M[3,3], M[3,4]]);
var 0..99: A11 = number([M[3,6], M[3,7]]);
var 0..9999: A13 = number([M[4,1], M[4,2], M[4,3], M[4,4]]);
var 0..9999: A15 = number([M[4,6], M[4,7], M[4,8], M[4,9]]);
var 0..9999: A17 = number([M[6,1], M[6,2], M[6,3], M[6,4]]);
var 0..9999: A20 = number([M[6,6], M[6,7], M[6,8], M[6,9]]);
var 0..99: A23 = number([M[7,3], M[7,4]]);
var 0..99: A24 = number([M[7,6], M[7,7]]);
var 0..99: A25 = number([M[8,1], M[8,2]]);
var 0..999: A27 = number([M[8,4], M[8,5], M[8,6]]);
var 0..99: A28 = number([M[8,8], M[8,9]]);
var 0..9999: A29 = number([M[9,1], M[9,2], M[9,3], M[9,4]]);
var 0..9999: A30 = number([M[9,6], M[9,7], M[9,8], M[9,9]]);
var 0..9999: D1 = number([M[1,1], M[2,1], M[3,1], M[4,1]]);
var 0..99: D2 = number([M[1,2], M[2,2]]);
var 0..9999: D3 = number([M[1,4], M[2,4], M[3,4], M[4,4]]);
var 0..9999: D4 = number([M[1,6], M[2,6], M[3,6], M[4,6]]);
var 0..99: D5 = number([M[1,8], M[2,8]]);
var 0..9999: D6 = number([M[1,9], M[2,9], M[3,9], M[4,9]]);
var 0..99: D10 = number([M[3,3], M[4,3]]);
var 0..99: D12 = number([M[3,7], M[4,7]]);
var 0..999: D14 = number([M[4,2], M[5,2], M[6,2]]);
var 0..999: D16 = number([M[4,8], M[5,8], M[6,8]]);
var 0..9999: D17 = number([M[6,1], M[7,1], M[8,1], M[9,1]]);
var 0..99: D18 = number([M[6,3], M[7,3]]);
var 0..9999: D19 = number([M[6,4], M[7,4], M[8,4], M[9,4]]);
var 0..9999: D20 = number([M[6,6], M[7,6], M[8,6], M[9,6]]);
var 0..99: D21 = number([M[6,7], M[7,7]]);
var 0..9999: D22 = number([M[6,9], M[7,9], M[8,9], M[9,9]]);
var 0..99: D26 = number([M[8,2], M[9,2]]);
var 0..99: D28 = number([M[8,8], M[9,8]]);

% 1 across: 27 across times two
constraint A1 = 2 * A27;

% 4 across: 4 down plus seventy-one
constraint A4 = D4 + 71;

% 7 across: 18 down plus four
constraint A7 = D18 + 4;

% 8 across: 6 down divided by sixteen
constraint D6 = 16 * A8;

% 9 across: 2 down minus eighteen
constraint A9 = D2 - 18;

% 10 across: Dozen in six gross
constraint A10 = 72;

% 11 across: 5 down minus seventy
constraint A11 = D5 - 70;

% 13 across: 26 down times 23 across
constraint A13 = D26 * A23;

% 15 across: 6 down minus 350
constraint A15 = D6 - 350;

% 17 across: 25 across times 23 across
constraint A17 = A25 * A23;

% 20 across: a square number
constraint exists(k in 0..99)(A20 = k * k);

% 23 across: a prime number
constraint A23 > 1 /\ forall(d in 2..99)(d = A23 \/ A23 mod d != 0);

% 24 across: a square number
constraint exists(k in 0..99)(A24 = k * k);

% 25 across: 20 across divided by seventeen
constraint A20 = 17 * A25;

% 27 across: 6 down divided by four
constraint D6 = 4 * A27;

% 28 across: four dozen
constraint A28 = 48;

% 29 across: seven gross
constraint A29 = 1008;

% 30 across: 22 down plus 450
constraint A30 = D22 + 450;

% 1 down: 1 across plus twenty-seven
constraint D1 = A1 + 27;

% 2 down: five dozen
constraint D2 = 60;

% 3 down: 30 across plus 888
constraint D3 = A30 + 888;

% 4 down: two times 17 across
constraint D4 = 2 * A17;

% 5 down: 29 across divided by twelve
constraint A29 = 12 * D5;

% 6 down: 28 across times 23 across
constraint D6 = A28 * A23;

% 10 down: 10 across plus four
constraint D10 = A10 + 4;

% 12 down: three times 24 across
constraint D12 = 3 * A24;

% 14 down: 13 across divided by sixteen
constraint A13 = 16 * D14;

% 16 down: 28 down times fifteen
constraint D16 = 15 * D28;

% 17 down: 13 across minus 399
constraint D17 = A13 - 399;

% 18 down: 29 across divided by eighteen
constraint A29 = 18 * D18;

% 19 down: 22 down minus ninety-four
constraint D19 = D22 - 94;

% 20 down: 20 across minus nine
constraint D20 = A20 - 9;

% 21 down: 25 across minus fifty-two
constraint D21 = A25 - 52;

% 22 down: 20 down times six
constraint D22 = 6 * D20;

% 26 down: five times 24 across
constraint D26 = 5 * A24;

% 28 down: 21 down plus twenty-seven
constraint D28 = D21 + 27;

solve satisfy;

output ["{\"M\": ", showJSON(M), "}"];
