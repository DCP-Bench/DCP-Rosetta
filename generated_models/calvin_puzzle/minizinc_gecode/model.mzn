% calvin_puzzle: a MiniZinc model from DCP Rosetta.
%
% Take an n by n grid of n^2 squares and fill every square with the numbers 1 to n^2, each used once, in
% sequence, starting from any square. If the next number is placed vertically or horizontally, it must be
% placed exactly three squares away from the previous number (a two square gap between them). If the next
% number is placed diagonally, it must be placed exactly two squares away from the previous number (a one
% square gap between them).
%
% Save this file as model.mzn. Download `calvin_puzzle.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py calvin_puzzle.json
%   minizinc model.mzn calvin_puzzle_1.json

include "globals.mzn";

int: n;                                      % the grid is n by n

set of int: Rows = 1..n;
set of int: Cols = 1..n;
set of int: Squares = 1..n*n;                % the squares, numbered row by row
set of int: Numbers = 1..n*n;                % the numbers placed on the grid

% the row and the column of square s
function int: row_of(int: s) = (s - 1) div n + 1;
function int: col_of(int: s) = (s - 1) mod n + 1;

% the move from square s to square t is a legal step: three squares horizontally or vertically,
% or two squares diagonally
function bool: legal_step(int: s, int: t) =
    let {
        int: dr = abs(row_of(t) - row_of(s)),
        int: dc = abs(col_of(t) - col_of(s))
    } in (dr = 3 /\ dc = 0) \/ (dr = 0 /\ dc = 3) \/ (dr = 2 /\ dc = 2);

% the legal steps as pairs [s, t], flattened row by row
array[int] of int: step_list = [v | s in Squares, t in Squares, v in [s, t] where legal_step(s, t)];
int: num_steps = length(step_list) div 2;   % the number of legal steps
array[1..num_steps, 1..2] of int: Steps = array2d(1..num_steps, 1..2, step_list);

% at[k]: the square holding number k
array[Numbers] of var Squares: at;

% x[r,c]: the number written in row r, column c
array[Rows, Cols] of var Numbers: x;

% every square holds one number
constraint all_different(at);

% x is the inverse of at
constraint inverse(array1d(x), at);

% each number is placed one legal step from the previous number
constraint forall(k in 1..n*n-1)(table([at[k], at[k+1]], Steps));

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
