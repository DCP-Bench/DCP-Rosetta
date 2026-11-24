% minesweeper: a MiniZinc model from DCP Rosetta.
%
% Minesweeper rules are very simple. The board is divided into cells, with mines randomly distributed. To
% win, you need to open all the cells. The number on a cell shows the number of mines adjacent to it. Using
% this information, you can determine cells that are safe, and cells that contain mines. Cells suspected of
% being mines can be marked with a flag using the right mouse button. The task is to determine which 'X'
% fields contain mines based on the provided numerical clues.
%
% Save this file as model.mzn. Download `minesweeper.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py minesweeper.json
%   minizinc model.mzn minesweeper_1.json

int: X;                                          % the value of a cell that is not opened
array[int,int] of int: game_data;                % game_data[r,c]: the number shown on cell (r,c), or X

set of int: Rows = index_set_1of2(game_data);    % the rows of the board
set of int: Columns = index_set_2of2(game_data); % the columns of the board

% mines[r,c]: cell (r,c) contains a mine
array[Rows, Columns] of var bool: mines;

% a cell that is opened is not a mine
constraint forall(r in Rows, c in Columns where game_data[r,c] != X)(not mines[r,c]);

% the number on an opened cell is the number of mines among its adjacent cells
constraint forall(r in Rows, c in Columns where game_data[r,c] != X)(
    sum(a in max(min(Rows), r - 1)..min(max(Rows), r + 1),
        b in max(min(Columns), c - 1)..min(max(Columns), c + 1) where not (a = r /\ b = c))
        (bool2int(mines[a,b])) = game_data[r,c]);

solve satisfy;

output ["{\"mines\": ", showJSON(mines), "}"];
