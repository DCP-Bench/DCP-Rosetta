% csplib_057_killer_sudoku: a MiniZinc model from DCP Rosetta.
%
% Killer sudoku (also killer su doku, sumdoku, sum doku, addoku, or samunamupure) is a puzzle that combines
% elements of sudoku and kakuro. Fill the grid with numbers from 1 to 9 so that each row, column and nonet
% contains each number exactly once, the sum of all numbers in a cage matches the small number given in its
% corner, and no number appears more than once in a cage.
%
% Save this file as model.mzn. Download `csplib_057_killer_sudoku.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_057_killer_sudoku.json
%   minizinc model.mzn csplib_057_killer_sudoku_1.json

include "globals.mzn";

int: n;                                          % the side of the grid, 9 in a standard killer sudoku
int: b = 3;                                      % the side of a nonet, a 3 x 3 block

set of int: N = 1..n;                            % the rows, the columns and the numbers
set of int: Nonets = 1..n div b;                 % the nonets along one side of the grid
set of int: Cages = index_set(problem_1);        % the cages

% problem_1[k]: the sum of the numbers in cage k (converted from the rows of the data)
array[int] of int: problem_1;
% problem_2[k,m,1..2]: the row and column of the m-th cell of cage k, padded with [0, 0]
array[int, int, int] of int: problem_2;
% problem_2_len[k]: the number of cells in cage k
array[int] of int: problem_2_len;

% x[r,c]: the number in row r, column c
array[N, N] of var N: x;

% each row contains each number exactly once
constraint forall(r in N)(all_different([x[r, c] | c in N]));

% each column contains each number exactly once
constraint forall(c in N)(all_different([x[r, c] | r in N]));

% each nonet contains each number exactly once
constraint forall(i, j in Nonets)(
    all_different([x[r, c] | r in (i - 1) * b + 1..i * b, c in (j - 1) * b + 1..j * b]));

% the numbers in each cage sum to the number printed in its corner
constraint forall(k in Cages)(
    sum(m in 1..problem_2_len[k])(x[problem_2[k, m, 1], problem_2[k, m, 2]]) = problem_1[k]);

% no number appears more than once in a cage
constraint forall(k in Cages)(
    all_different([x[problem_2[k, m, 1], problem_2[k, m, 2]] | m in 1..problem_2_len[k]]));

solve satisfy;
output ["{\"x\": ", showJSON(x), "}"];
