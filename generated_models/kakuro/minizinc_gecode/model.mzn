% kakuro: a MiniZinc model from DCP Rosetta.
%
% The object of the puzzle is to insert a digit from 1 to 9 inclusive into each white cell such that the
% sum of the numbers in each entry matches the clue associated with it, and no digit is duplicated in any
% entry. By an unwritten rule of puzzle making, each clue has at least two numbers that add up to it (not enforced by the model).
%
% Save this file as model.mzn. Download `kakuro.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py kakuro.json
%   minizinc model.mzn kakuro_1.json

include "globals.mzn";

int: n;                                          % the grid is n by n
array[int, int] of int: blanks;                  % blanks[b,1..2]: row and column of black cell b

% problem_1[p]: the clue (the sum) of entry p
array[int] of int: problem_1;
% problem_2[p,k,1..2]: row and column of the k-th white cell of entry p (padded with 0 after its last cell)
array[int, int, int] of int: problem_2;
% problem_2_len[p]: the number of white cells of entry p
array[int] of int: problem_2_len;

set of int: Rows = 1..n;                         % grid rows
set of int: Cols = 1..n;                         % grid columns
set of int: Entries = index_set(problem_1);      % the across and down entries
set of int: Digits = 1..9;                       % the digits to place

% x[r,c]: the digit in row r, column c; a black cell is 0
array[Rows, Cols] of var 0..9: x;

% the black cells are 0
constraint forall(b in index_set_1of2(blanks))(x[blanks[b, 1], blanks[b, 2]] = 0);

% every white cell holds a digit from 1 to 9
constraint forall(p in Entries, k in 1..problem_2_len[p])(
    x[problem_2[p, k, 1], problem_2[p, k, 2]] in Digits);

% the digits of each entry sum to its clue
constraint forall(p in Entries)(
    sum(k in 1..problem_2_len[p])(x[problem_2[p, k, 1], problem_2[p, k, 2]]) = problem_1[p]);

% no digit is duplicated within an entry
constraint forall(p in Entries)(
    all_different([x[problem_2[p, k, 1], problem_2[p, k, 2]] | k in 1..problem_2_len[p]]));

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
