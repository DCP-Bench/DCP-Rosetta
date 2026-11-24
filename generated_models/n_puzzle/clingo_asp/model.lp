% n_puzzle: a clingo model from DCP Rosetta.
%
% The N-Puzzle is a classic sliding puzzle game where the goal is to move tiles on a grid to achieve a specific end configuration. The puzzle consists of a grid with n+1 tiles, one of which is empty. The objective is to trace the steps to the original picture by moving the tiles into their correct positions. Input includes the start and end state of the puzzle, in which 0 is the empty tile, along with the number of steps to the solution, which includes the start and end states. Each step moves one tile that is horizontally or vertically next to the empty tile into the empty position. Also, "freezing" is not allowed, meaning that the state of the puzzle must change at each step.
%
% Save this file as model.lp. Download `n_puzzle.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py n_puzzle.json
%   python -m clingo model.lp n_puzzle_1.lp
%
% Input: n_STEPS(N) the number of steps N, start and end states included; puzzle_start(I, J, V) and
% puzzle_end(I, J, V) the tile V in row I and column J of the start and end state, 0 being the empty tile
% (indices are 0-based, as in the data).

cell(I,J) :- puzzle_start(I,J,_).
time(0..N-1) :- n_STEPS(N).

% neighbour(I,J,I2,J2): the cells (I,J) and (I2,J2) are horizontally or vertically next to each other
neighbour(I,J,I2,J2) :- cell(I,J), cell(I2,J2), |I-I2| + |J-J2| == 1.

% blank(T,I,J): the empty tile is in row I and column J at step T
blank(0,I,J) :- puzzle_start(I,J,0).

% each step after the first moves the empty tile into a neighbouring cell, so the state changes at every step
1 { blank(T,I2,J2) : neighbour(I1,J1,I2,J2) } 1 :- time(T), T > 0, blank(T-1,I1,J1).

% steps(T,I,J,V): the tile V is in row I and column J at step T
% the state at step 0 is the start state
steps(0,I,J,V) :- puzzle_start(I,J,V).

% the tile in the cell the empty tile moves into goes to the cell the empty tile leaves
steps(T,I1,J1,V) :- time(T), T > 0, blank(T-1,I1,J1), blank(T,I2,J2), steps(T-1,I2,J2,V).

% the empty tile is in its new cell
steps(T,I,J,0) :- time(T), T > 0, blank(T,I,J).

% every other tile stays where it was
steps(T,I,J,V) :- time(T), T > 0, steps(T-1,I,J,V), not blank(T-1,I,J), not blank(T,I,J).

% the state at the last step is the end state
:- n_STEPS(N), puzzle_end(I,J,V), not steps(N-1,I,J,V).

#show steps/4.
