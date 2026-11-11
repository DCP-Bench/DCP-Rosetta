% csplib_032_max_density_still_life: a MiniZinc model from DCP Rosetta.
%
% This problem, arising from Conway's Game of Life, seeks to find the most densely populated stable pattern (a "still
% life") on an n x m active grid. A still life is a pattern of live and dead cells that does not change from one
% generation to the next. Life is played on an infinite board. Cells outside the n x m active grid are dead, but they
% are still part of the board.
%
% The rules for a pattern to be a still life are:
% 1. A live cell must have exactly 2 or 3 live neighbors to remain alive.
% 2. A dead cell, including any dead cell just outside the active grid, must not have exactly 3 live neighbors
%    (otherwise it would become alive).
%
% The goal is to maximize the number of live cells in the active grid.
%
% Save this file as model.mzn. Download `csplib_032_max_density_still_life.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_032_max_density_still_life.json
%   minizinc model.mzn csplib_032_max_density_still_life_1.json

int: n;                                              % the number of rows of the active grid
int: m;                                              % the number of columns of the active grid
set of int: Rows = 1..n;                             % the rows of the active grid
set of int: Cols = 1..m;                             % the columns of the active grid
set of int: PadRows = 0..n + 1;                      % the active grid with its ring of dead cells around it
set of int: PadCols = 0..m + 1;
set of int: Frame = -1..n + 2;                       % the rows and columns the neighbour counts look at

% live[i,j]: the cell in row i and column j is alive; the cells around the active grid are dead
array[Frame, Frame] of var bool: live;
% neighbours[i,j]: the live neighbours of the cell in row i and column j
array[PadRows, PadCols] of var 0..8: neighbours =
    array2d(PadRows, PadCols, [sum(di in -1..1, dj in -1..1 where di != 0 \/ dj != 0)(bool2int(live[i + di, j + dj]))
                               | i in PadRows, j in PadCols]);

% the cells outside the active grid are dead
constraint forall(i in Frame, j in Frame where i < 1 \/ i > n \/ j < 1 \/ j > m)(not live[i, j]);

% a live cell has exactly 2 or 3 live neighbours
constraint forall(i in PadRows, j in PadCols)(live[i, j] -> neighbours[i, j] in 2..3);

% a dead cell does not have exactly 3 live neighbours
constraint forall(i in PadRows, j in PadCols)(not live[i, j] -> neighbours[i, j] != 3);

% the number of live cells in the active grid
var int: objective = sum(i in Rows, j in Cols)(bool2int(live[i, j]));

solve maximize objective;

% grid[i,j]: the cell in row i and column j of the active grid is alive
array[Rows, Cols] of var bool: grid = array2d(Rows, Cols, [live[i, j] | i in Rows, j in Cols]);

output ["{\"grid\": ", showJSON(grid), "}"];
