% csplib_014_solitaire_battleships: a MiniZinc model from DCP Rosetta.
%
% The Battleships puzzle is played on a grid. The fleet consists of battleships (four squares
% long), cruisers (three squares long), destroyers (two squares long) and submarines (one square).
% Ships may be oriented horizontally or vertically, and no two ships occupy adjacent squares, not
% even diagonally. The digits along the right side of and below the grid give the number of squares
% in the corresponding row or column that are occupied by vessels. Some puzzles have shots already
% taken: these may show water, a complete submarine, or a part of a longer vessel. Find the grid,
% where each square is water, a submarine, or a ship part (left, right, top, bottom or middle).
%
% Save this file as model.mzn. Download `csplib_014_solitaire_battleships.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_014_solitaire_battleships.json
%   minizinc model.mzn csplib_014_solitaire_battleships_1.json

int: rows;                                   % the number of rows
int: cols;                                   % the number of columns
array[int] of int: rowsum;                   % rowsum[r + 1]: occupied squares in row r
array[int] of int: colsum;                   % colsum[c + 1]: occupied squares in column c
array[int, 1..2] of int: fleet_counts;       % each row: [ship size, number of ships of that size]
array[int, 1..3] of int: hints;              % each row: [row, column, content] of a shot square

int: WATER;                                  % the codes of the square contents
int: CIRCLE;                                 % a submarine
int: LEFT;                                   % the left end of a horizontal ship
int: RIGHT;                                  % the right end of a horizontal ship
int: TOP;                                    % the top end of a vertical ship
int: BOTTOM;                                 % the bottom end of a vertical ship
int: MIDDLE;                                 % a square inside a ship of three or more squares

set of int: Rows = 0..rows - 1;              % rows and columns are numbered from 0
set of int: Cols = 0..cols - 1;
set of int: Contents = {WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE};

% grid[r, c]: the content of the square in row r, column c
array[Rows, Cols] of var Contents: grid;

% the square (r, c) lies inside the grid
predicate in_grid(int: r, int: c) = r >= 0 /\ r < rows /\ c >= 0 /\ c < cols;

% the square (r, c) is water, or lies outside the grid
predicate water_or_off_grid(int: r, int: c) = if in_grid(r, c) then grid[r, c] = WATER else true endif;

% the square (r, c) is inside the grid and holds one of the given contents
predicate piece_at(int: r, int: c, set of int: pieces) = if in_grid(r, c) then grid[r, c] in pieces else false endif;

% the shots already taken are as given
constraint forall(h in index_set_1of2(hints))(grid[hints[h, 1], hints[h, 2]] = hints[h, 3]);

% each row contains the listed number of occupied squares
constraint forall(r in Rows)(sum(c in Cols)(bool2int(grid[r, c] != WATER)) = rowsum[r + 1]);

% each column contains the listed number of occupied squares
constraint forall(c in Cols)(sum(r in Rows)(bool2int(grid[r, c] != WATER)) = colsum[c + 1]);

% no two ships touch, not even diagonally: the diagonal neighbours of every occupied square are water
constraint forall(r in Rows, c in Cols)(grid[r, c] != WATER ->
    (water_or_off_grid(r - 1, c - 1) /\ water_or_off_grid(r - 1, c + 1) /\
     water_or_off_grid(r + 1, c - 1) /\ water_or_off_grid(r + 1, c + 1)));

% a submarine is a ship of one square, so its orthogonal neighbours are water
constraint forall(r in Rows, c in Cols)(grid[r, c] = CIRCLE ->
    (water_or_off_grid(r - 1, c) /\ water_or_off_grid(r + 1, c) /\
     water_or_off_grid(r, c - 1) /\ water_or_off_grid(r, c + 1)));

% a left end has a middle or right end to its right, and water on its other three sides
constraint forall(r in Rows, c in Cols)(grid[r, c] = LEFT ->
    (piece_at(r, c + 1, {MIDDLE, RIGHT}) /\ water_or_off_grid(r, c - 1) /\
     water_or_off_grid(r - 1, c) /\ water_or_off_grid(r + 1, c)));

% a right end has a middle or left end to its left, and water on its other three sides
constraint forall(r in Rows, c in Cols)(grid[r, c] = RIGHT ->
    (piece_at(r, c - 1, {MIDDLE, LEFT}) /\ water_or_off_grid(r, c + 1) /\
     water_or_off_grid(r - 1, c) /\ water_or_off_grid(r + 1, c)));

% a top end has a middle or bottom end below it, and water on its other three sides
constraint forall(r in Rows, c in Cols)(grid[r, c] = TOP ->
    (piece_at(r + 1, c, {MIDDLE, BOTTOM}) /\ water_or_off_grid(r - 1, c) /\
     water_or_off_grid(r, c - 1) /\ water_or_off_grid(r, c + 1)));

% a bottom end has a middle or top end above it, and water on its other three sides
constraint forall(r in Rows, c in Cols)(grid[r, c] = BOTTOM ->
    (piece_at(r - 1, c, {MIDDLE, TOP}) /\ water_or_off_grid(r + 1, c) /\
     water_or_off_grid(r, c - 1) /\ water_or_off_grid(r, c + 1)));

% a middle square lies in a horizontal ship (left or middle to its left, right or middle to
% its right, water above and below) or in a vertical ship (top or middle above, bottom or
% middle below, water to the left and right)
constraint forall(r in Rows, c in Cols)(grid[r, c] = MIDDLE ->
    ((piece_at(r, c - 1, {LEFT, MIDDLE}) /\ piece_at(r, c + 1, {RIGHT, MIDDLE}) /\
      water_or_off_grid(r - 1, c) /\ water_or_off_grid(r + 1, c))
     \/
     (piece_at(r - 1, c, {TOP, MIDDLE}) /\ piece_at(r + 1, c, {BOTTOM, MIDDLE}) /\
      water_or_off_grid(r, c - 1) /\ water_or_off_grid(r, c + 1))));

% the number of submarines is the number of ships of size 1 in the fleet
constraint sum(r in Rows, c in Cols)(bool2int(grid[r, c] = CIRCLE)) =
           sum(k in index_set_1of2(fleet_counts) where fleet_counts[k, 1] = 1)(fleet_counts[k, 2]);

% for each ship size s >= 2, the number of ships of that size is the listed count: a horizontal
% ship is a left end, s - 2 middles and a right end in a row, a vertical one a top end, s - 2
% middles and a bottom end in a column
constraint forall(k in index_set_1of2(fleet_counts) where fleet_counts[k, 1] >= 2)(
    let { int: s = fleet_counts[k, 1] } in
    sum(r in Rows, c in 0..cols - s)
        (bool2int(grid[r, c] = LEFT /\ grid[r, c + s - 1] = RIGHT /\ forall(j in 1..s - 2)(grid[r, c + j] = MIDDLE)))
    + sum(r in 0..rows - s, c in Cols)
        (bool2int(grid[r, c] = TOP /\ grid[r + s - 1, c] = BOTTOM /\ forall(j in 1..s - 2)(grid[r + j, c] = MIDDLE)))
    = fleet_counts[k, 2]);

% every left or top end starts a ship of a size in the fleet, so no other ships exist
constraint sum(r in Rows, c in Cols)(bool2int(grid[r, c] = LEFT \/ grid[r, c] = TOP)) =
           sum(k in index_set_1of2(fleet_counts) where fleet_counts[k, 1] >= 2)(fleet_counts[k, 2]);

solve satisfy;
output ["{\"grid\": ", showJSON(grid), "}"];
