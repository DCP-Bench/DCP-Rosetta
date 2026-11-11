% flow_free_game: a MiniZinc model from DCP Rosetta.
%
% Connect matching colours with pipes to create a flow. Pair all colours, and cover the entire board.
% Pipes break if they cross or overlap. The cells with a value of 0 are empty and need to be filled
% with a colour. Cells are connected horizontally and vertically: a numbered cell has exactly one
% neighbour of its own colour, and a filled cell has exactly two.
%
% Save this file as model.mzn. Download `flow_free_game.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py flow_free_game.json
%   minizinc model.mzn flow_free_game_1.json

array[int,int] of int: board;                        % board[i,j]: colour of a numbered cell, 0 if empty
set of int: Rows = index_set_1of2(board);            % one index per row
set of int: Columns = index_set_2of2(board);         % one index per column
int: n_colors = max(board);                          % colours are numbered 1..n_colors
int: n_cells = card(Rows) * card(Columns);           % the number of cells on the board

% B[i,j]: colour of cell (i,j)
array[Rows, Columns] of var 1..n_colors: B;
% D[i,j]: position of cell (i,j) along its pipe, counted from a numbered cell at position 1
array[Rows, Columns] of var 1..n_cells: D;

% a numbered cell keeps its colour
constraint forall(i in Rows, j in Columns where board[i,j] != 0)(B[i,j] = board[i,j]);

% a numbered cell is the start of its pipe
constraint forall(i in Rows, j in Columns where board[i,j] != 0)(D[i,j] = 1);

% a filled cell is not a start of its pipe
constraint forall(i in Rows, j in Columns where board[i,j] = 0)(D[i,j] >= 2);

% a numbered cell has exactly one neighbour of its own colour
constraint forall(i in Rows, j in Columns where board[i,j] != 0)(
    sum(a in Rows, b in Columns where abs(a - i) + abs(b - j) = 1)(bool2int(B[a,b] = B[i,j])) = 1);

% a filled cell has exactly two neighbours of its own colour
constraint forall(i in Rows, j in Columns where board[i,j] = 0)(
    sum(a in Rows, b in Columns where abs(a - i) + abs(b - j) = 1)(bool2int(B[a,b] = B[i,j])) = 2);

% each filled cell continues the pipe from a neighbour one position closer to its start,
% so every pipe is one connected path, with no loop apart from it
constraint forall(i in Rows, j in Columns where board[i,j] = 0)(
    exists(a in Rows, b in Columns where abs(a - i) + abs(b - j) = 1)(B[a,b] = B[i,j] /\ D[a,b] = D[i,j] - 1));

solve satisfy;

output ["{\"B\": ", showJSON(B), "}"];
