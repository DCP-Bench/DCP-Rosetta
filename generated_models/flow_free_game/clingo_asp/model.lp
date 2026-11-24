% flow_free_game: a clingo model from DCP Rosetta.
%
% Connect matching colors with pipe to create a flow. Pair all colors, and cover the entire board to solve
% each puzzle in Flow Free. But watch out, pipes will break if they cross or overlap! The cells with a value
% of 0 are empty and need to be filled with a color. Cells are connected horizontally and vertically: a
% numbered cell has exactly one neighbour of its own color, and a filled cell has exactly two.
%
% Save this file as model.lp. Download `flow_free_game.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py flow_free_game.json
%   python -m clingo model.lp flow_free_game_1.lp
%
% Input: board(I, J, C) holds the color C of the cell in row I and column J (indices are 0-based, as in
% the data); C is 0 when the cell is empty and has to be filled.

cell(I, J) :- board(I, J, _).

% two cells are neighbours when they are next to each other horizontally or vertically
neighbour(I, J, K, L) :- cell(I, J), cell(K, L), |K - I| + |L - J| = 1.

% the colors are those of the numbered cells on the board
color(C) :- board(_, _, C), C > 0.

% each cell gets exactly one color: b(I, J, C) holds when cell (I, J) has color C
1 { b(I, J, C) : color(C) } 1 :- cell(I, J).

% a numbered cell keeps its color
:- board(I, J, C), C > 0, not b(I, J, C).

% a numbered cell has exactly one neighbour of its own color
:- board(I, J, C), C > 0, #count { K, L : neighbour(I, J, K, L), b(K, L, C) } != 1.

% a filled cell has exactly two neighbours of its own color
:- board(I, J, 0), b(I, J, C), #count { K, L : neighbour(I, J, K, L), b(K, L, C) } != 2.

% every cell of a color is connected to a numbered cell of that color, so no pipe is a loop without an end
reach(I, J, C) :- board(I, J, C), C > 0.
reach(K, L, C) :- reach(I, J, C), neighbour(I, J, K, L), b(K, L, C).
:- b(I, J, C), not reach(I, J, C).

#show b/3.
