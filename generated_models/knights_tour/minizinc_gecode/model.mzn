% knights_tour: a MiniZinc model from DCP Rosetta.
%
% A knight's tour is a sequence of moves of a knight on a chessboard such that the knight visits every
% square exactly once (without returning to the starting square). Find a knight's tour on an n x n
% chessboard.
%
% Save this file as model.mzn. Download `knights_tour.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py knights_tour.json
%   minizinc model.mzn knights_tour_1.json

include "globals.mzn";

int: n;                                         % the size of the chessboard

int: squares = n * n;                           % the number of squares on the board
set of int: Squares = 1..squares;               % squares numbered row by row: (row-1)*n + column
int: end_mark = squares + 1;                    % an extra node standing for "the tour is over"

% the eight moves of a knight (row offset, column offset)
set of int: Moves = 1..8;
array[Moves] of int: move_row = [2, 2, -2, -2, 1, 1, -1, -1];
array[Moves] of int: move_col = [1, -1, 1, -1, 2, -2, 2, -2];

% moves[s]: the squares a knight can jump to from square s without leaving the board
array[Squares] of set of int: moves =
    [ { (i + move_row[m] - 1) * n + (j + move_col[m])
      | m in Moves where i + move_row[m] in 1..n /\ j + move_col[m] in 1..n }
    | i in 1..n, j in 1..n ];

% next_square[s]: the square the knight goes to after square s; the last square
% goes to the extra node and the extra node goes to the first square
array[1..end_mark] of var 1..end_mark: next_square;

% the knight's moves form a single cycle through all squares and the extra node,
% so the knight visits every square exactly once
constraint circuit(next_square);

% each move is a knight move (or the move that ends the tour)
constraint forall(s in Squares)(next_square[s] in moves[s] union {end_mark});

% move_number[s]: the move at which the knight is on square s; the first square is move 0
% and the extra node counts as move -1
array[1..end_mark] of var -1..squares - 1: move_number;
constraint move_number[end_mark] = -1;

% each move is numbered one higher than the move before it (the end of the tour is not numbered)
constraint forall(s in 1..end_mark)
    (next_square[s] = end_mark \/ move_number[next_square[s]] = move_number[s] + 1);

% every square has a different move number
constraint all_different(move_number);

% x[i,j]: the move number at which the knight is on the square in row i, column j
array[1..n, 1..n] of var 0..squares - 1: x;
constraint forall(i in 1..n, j in 1..n)(x[i, j] = move_number[(i - 1) * n + j]);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
