% coins_grid: a MiniZinc model from DCP Rosetta.
%
% In a quadratic grid (or a larger chessboard) n by n, one should place coins in such a way that the
% following conditions are fulfilled: in each row exactly c coins must be placed; in each column
% exactly c coins must be placed; the sum of the quadratic horizontal distance from the main diagonal
% of all cells containing a coin must be as small as possible, the distance of a coin in row i and
% column j being (i - j)^2; in each cell at most one coin can be placed.
%
% Save this file as model.mzn. Download `coins_grid.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py coins_grid.json
%   minizinc model.mzn coins_grid_1.json

int: n;  % side of the grid
int: c;  % coins in each row and in each column

set of int: Cells = 1..n;  % rows and columns of the grid

% x[i, j] = 1 if a coin is placed in cell (i, j), at most one coin per cell
array[Cells, Cells] of var 0..1: x;

% z: sum of the squared horizontal distances (i - j)^2 of the coins from the main diagonal
var 0..n * n * n * n: z = sum(i, j in Cells)(x[i, j] * (i - j) * (i - j));

% exactly c coins are placed in each row
constraint forall(i in Cells)(sum(j in Cells)(x[i, j]) = c);

% exactly c coins are placed in each column
constraint forall(j in Cells)(sum(i in Cells)(x[i, j]) = c);

% implied (redundant) constraint, not part of the problem: a row costs at least the c smallest squared
% distances among its cells, so z is at least the sum of these over all rows
int: cheapest = sum(i in Cells)(sum(k in 1..c)(sort([(i - j) * (i - j) | j in Cells])[k]));
constraint z >= cheapest;

var int: objective = z;

solve minimize objective;

output ["{\"x\": ", showJSON(x), ", \"z\": ", show(z), "}"];
