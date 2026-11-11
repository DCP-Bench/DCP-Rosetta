% Kakuro: fill the white cells of an n x n grid with digits 1..9 so that every
% entry (a run of white cells across or down, given by its clue) sums to its
% clue and holds no digit twice. Black (clue or blank) cells are output as 0.
include "globals.mzn";

int: n;                                   % size of the grid
array[int,int] of int: blanks;            % 1-based [row, column] of every black cell

% Each entry in the JSON is [clue, [r, c], [r, c], ...]. The runner binds it as
% three parameters: problem_1 holds the clues, problem_2 the cells of each entry
% (1 = row, 2 = column, padded with [0, 0] to the longest entry), and
% problem_2_len the number of real cells of each entry.
array[int] of int: problem_1;
array[int,int,int] of int: problem_2;
array[int] of int: problem_2_len;

set of int: Rows = 1..n;
set of int: Cols = 1..n;
set of int: Segs = index_set(problem_1);

% x[r, c] = digit in row r, column c; 0 for a black cell
array[Rows, Cols] of var 0..9: x;

% black cells are 0
constraint forall(b in index_set_1of2(blanks))(x[blanks[b, 1], blanks[b, 2]] = 0);

% every cell of an entry holds a digit 1..9
constraint forall(p in Segs, k in 1..problem_2_len[p])(
  x[problem_2[p, k, 1], problem_2[p, k, 2]] >= 1);

% each entry's cells sum to its clue and hold different digits
constraint forall(p in Segs)(
  let {
    array[int] of var int: cells =
      [x[problem_2[p, k, 1], problem_2[p, k, 2]] | k in 1..problem_2_len[p]];
  } in
    sum(cells) = problem_1[p] /\ all_different(cells));

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
