% csplib_032_max_density_still_life: a clingo model from DCP Rosetta.
%
% This problem, arising from Conway's Game of Life, seeks to find the most densely populated stable pattern (a "still life") on an n x m active grid. A still life is a pattern of live and dead cells that does not change from one generation to the next. Life is played on an infinite board. Cells outside the n x m active grid are dead and are not printed, but they are still part of the board. The rules for a pattern to be a still life are:
% 1. A live cell must have exactly 2 or 3 live neighbors to remain alive.
% 2. A dead cell, including any dead cell just outside the active grid, must not have exactly 3 live neighbors (otherwise it would become alive).
% The goal is to maximize the number of live cells in the active grid.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
% Save this file as model.lp. Download `csplib_032_max_density_still_life.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_032_max_density_still_life.json
%   python -m clingo model.lp csplib_032_max_density_still_life_1.lp

% Input: n(N) and m(M): the active grid has N rows and M columns (cells are numbered from 0).

% the active grid, and the board around it: the cells just outside the grid are the border
inside(I,J) :- n(N), m(M), I = 0..N-1, J = 0..M-1.
cell(I,J)   :- n(N), m(M), I = -1..N, J = -1..M.

% adj(I,J,I2,J2): cells (I,J) and (I2,J2) are neighbours (touching, including diagonally)
adj(I,J,I+D,J+E) :- cell(I,J), D = -1..1, E = -1..1, (D,E) != (0,0), cell(I+D,J+E).

% live(I,J): the cell (I,J) of the active grid is alive; a cell outside the grid is dead
{ live(I,J) } :- inside(I,J).

% a live cell has 2 or 3 live neighbours
:- live(I,J), #count { I2,J2 : live(I2,J2), adj(I,J,I2,J2) } < 2.
:- live(I,J), #count { I2,J2 : live(I2,J2), adj(I,J,I2,J2) } > 3.

% a dead cell, inside the grid or in the border around it, does not have exactly 3 live neighbours
:- cell(I,J), not live(I,J), #count { I2,J2 : live(I2,J2), adj(I,J,I2,J2) } = 3.

% the number of live cells in the active grid is as large as possible
#maximize { 1,I,J : live(I,J) }.

% grid(I,J,V): the cell (I,J) of the active grid holds V, 1 when alive and 0 when dead
grid(I,J,1) :- live(I,J).
grid(I,J,0) :- inside(I,J), not live(I,J).

#show grid/3.
