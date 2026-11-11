% futoshiki: a MiniZinc model from DCP Rosetta.
%
% The futoshiki puzzle is played on a square grid, such as 5 x 5. Place the numbers 1 to 5 (or whatever
% the dimensions are) so that each row and each column contains each of the digits once. Some digits
% may be given at the start. Inequality constraints are also specified between some of the squares,
% such that one must be higher or lower than its neighbour. These constraints must be honoured as the
% grid is filled out.
%
% Save this file as model.mzn. Download `futoshiki.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py futoshiki.json
%   minizinc model.mzn futoshiki_1.json

include "globals.mzn";

array[int,int] of int: values;      % values[r,c]: the digit given in cell (r,c), 0 if the cell is empty
array[int,int] of int: lt;          % lt[k,1..4] = r1, c1, r2, c2: cell (r1,c1) is smaller than cell (r2,c2)

set of int: Rows = index_set_1of2(values);      % one index per row
set of int: Cols = index_set_2of2(values);      % one index per column
int: n = card(Rows);                            % the grid is n x n, holding the digits 1..n
set of int: Digits = 1..n;

% grid[r,c]: the digit in cell (r,c)
array[Rows, Cols] of var Digits: grid;

% the given digits stay in their cells
constraint forall(r in Rows, c in Cols where values[r,c] > 0)(grid[r,c] = values[r,c]);

% each row contains each digit once
constraint forall(r in Rows)(all_different([grid[r,c] | c in Cols]));

% each column contains each digit once
constraint forall(c in Cols)(all_different([grid[r,c] | r in Rows]));

% each inequality sign is honoured: the first cell is smaller than the second
constraint forall(k in index_set_1of2(lt))(grid[lt[k,1], lt[k,2]] < grid[lt[k,3], lt[k,4]]);

solve satisfy;

output ["{\"grid\": ", showJSON(grid), "}"];
