% coins_grid: a clingo model from DCP Rosetta.
%
% In a square grid of n by n cells (or a larger chessboard), place coins so that each row holds exactly c coins
% and each column holds exactly c coins, with at most one coin per cell. The sum over all coins of the squared
% horizontal distance from the main diagonal, (i - j)^2 for a coin in row i and column j, must be as small as possible.
%
% Save this file as model.lp. Download `coins_grid.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py coins_grid.json
%   python -m clingo model.lp coins_grid_1.lp
%
% Input: n(N) holds the size N of the grid, and c(C) the number C of coins per row and per column
% (indices are 0-based, as in the data).

index(0..N-1) :- n(N).

% each cell either holds a coin or does not
{ coin(I,J) } :- index(I), index(J).

% each row holds exactly c coins
:- index(I), c(C), #count { J : coin(I,J) } != C.

% each column holds exactly c coins
:- index(J), c(C), #count { I : coin(I,J) } != C.

% the sum over all coins of the squared distance (I-J)^2 from the main diagonal is as small as possible
#minimize { (I-J)*(I-J), I, J : coin(I,J) }.

% z is that sum: the sum over all coins of the squared distance from the diagonal
z(Z) :- Z = #sum { (I-J)*(I-J), I, J : coin(I,J) }.

% x(I,J,1) when the cell in row I and column J holds a coin, x(I,J,0) when it does not
x(I,J,1) :- coin(I,J).
x(I,J,0) :- index(I), index(J), not coin(I,J).

#show x/3.
#show z/1.
