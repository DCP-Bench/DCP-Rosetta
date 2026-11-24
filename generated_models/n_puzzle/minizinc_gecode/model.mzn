% n_puzzle: a MiniZinc model from DCP Rosetta.
%
% The N-Puzzle is a classic sliding puzzle game where the goal is to move tiles on a grid to achieve a
% specific end configuration. The puzzle consists of a grid with n+1 tiles, one of which is empty. The
% objective is to trace the steps to the original picture by moving the tiles into their correct
% positions. The start and end state of the puzzle are given, in which 0 is the empty tile, along with the
% number of steps to the solution, which includes the start and end states. Each step moves one tile that
% is horizontally or vertically next to the empty tile into the empty position. Freezing is not allowed,
% meaning that the state of the puzzle must change at each step.
%
% Save this file as model.mzn. Download `n_puzzle.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py n_puzzle.json
%   minizinc model.mzn n_puzzle_1.json

include "globals.mzn";

int: N_STEPS;                                     % the number of states, start and end included
array[int,int] of int: puzzle_start;               % the start state; 0 is the empty tile
array[int,int] of int: puzzle_end;                 % the end state; 0 is the empty tile

set of int: Pos = index_set_1of2(puzzle_start);    % the rows and the columns of the grid
set of int: Tiles = 0..card(Pos) * card(Pos) - 1;  % the tiles, 0 for the empty one
set of int: Steps = 1..N_STEPS;                    % the states of the puzzle, numbered from 1

% steps[t,i,j]: the tile in row i, column j of the grid in state t
array[Steps, Pos, Pos] of var Tiles: steps;

% the first state is the start state
constraint forall(i, j in Pos)(steps[1,i,j] = puzzle_start[i,j]);

% the last state is the end state
constraint forall(i, j in Pos)(steps[N_STEPS,i,j] = puzzle_end[i,j]);

% each state uses every tile exactly once
constraint forall(t in Steps)(all_different([steps[t,i,j] | i, j in Pos]));

% each step moves one tile that is horizontally or vertically next to the empty tile into the empty position
constraint forall(t in 2..N_STEPS, i, j in Pos)(
    steps[t,i,j] = 0 ->
        exists(a, b in Pos where abs(a - i) + abs(b - j) = 1)(steps[t - 1,a,b] = 0));

% a square that is neither empty before nor empty after the step keeps its tile
constraint forall(t in 2..N_STEPS, i, j in Pos)(
    steps[t - 1,i,j] = 0 \/ steps[t,i,j] = 0 \/ steps[t - 1,i,j] = steps[t,i,j]);

% the state must change at each step (no freezing)
constraint forall(t in 2..N_STEPS)(exists(i, j in Pos)(steps[t - 1,i,j] != steps[t,i,j]));

solve satisfy;

output ["{\"steps\": ", showJSON(steps), "}"];
