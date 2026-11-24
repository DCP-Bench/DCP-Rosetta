% kenken: a MiniZinc model from DCP Rosetta.
%
% KenKen is a style of arithmetic and logical puzzle sharing several characteristics with sudoku. The
% objective is to fill the grid with the digits 1 through n such that each row and each column contains
% exactly one of each digit, and each bold-outlined group of cells (a cage) contains digits that achieve
% the cage's result by its mathematical operation: addition, subtraction, multiplication or division.
% Unlike in Killer sudoku, digits may repeat within a cage. Here the operations are not given: a cage of
% one cell holds its result, a cage of two cells may use any of the four operations (a division must be
% exact), and a larger cage uses either addition or multiplication.
%
% Save this file as model.mzn. Download `kenken.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py kenken.json
%   minizinc model.mzn kenken_1.json

include "globals.mzn";

int: n;                                          % the grid is n by n, with digits 1..n

% problem_1[c]: the result of cage c
array[int] of int: problem_1;
% problem_2[c,k,1..2]: row and column of the k-th cell of cage c (padded with 0 after its last cell)
array[int, int, int] of int: problem_2;
% problem_2_len[c]: the number of cells of cage c
array[int] of int: problem_2_len;

set of int: Rows = 1..n;                         % grid rows
set of int: Cols = 1..n;                         % grid columns
set of int: Digits = 1..n;                       % the digits to place
set of int: Cages = index_set(problem_1);        % the cages

% x[r,c]: the digit in row r, column c
array[Rows, Cols] of var Digits: x;

% each row contains each digit exactly once
constraint forall(r in Rows)(all_different([x[r, c] | c in Cols]));
% each column contains each digit exactly once
constraint forall(c in Cols)(all_different([x[r, c] | r in Rows]));

% a cage of one cell holds its result
constraint forall(c in Cages where problem_2_len[c] = 1)(
    x[problem_2[c, 1, 1], problem_2[c, 1, 2]] = problem_1[c]);

% a cage of two cells reaches its result by addition, multiplication, subtraction or exact division
constraint forall(c in Cages where problem_2_len[c] = 2)(
    let {
        var Digits: a = x[problem_2[c, 1, 1], problem_2[c, 1, 2]];
        var Digits: b = x[problem_2[c, 2, 1], problem_2[c, 2, 2]];
        int: t = problem_1[c];
    } in
    a + b = t \/ a * b = t \/ a - b = t \/ b - a = t \/ a = t * b \/ b = t * a);

% a larger cage reaches its result by addition or multiplication of its cells
constraint forall(c in Cages where problem_2_len[c] > 2)(
    let {
        array[1..problem_2_len[c]] of var Digits: cells =
            [x[problem_2[c, k, 1], problem_2[c, k, 2]] | k in 1..problem_2_len[c]];
    } in
    sum(cells) = problem_1[c] \/ product(cells) = problem_1[c]);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
