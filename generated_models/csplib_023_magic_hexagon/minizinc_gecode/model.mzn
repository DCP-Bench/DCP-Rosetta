% csplib_023_magic_hexagon: a MiniZinc model from DCP Rosetta.
%
% A magic hexagon problem involves arranging the numbers 1 to 19 in a hexagonal pattern
% such that the sum of the numbers in each of the 15 lines (rows and diagonals) is
% equal to a magic constant, which is 38.
%
% The hexagonal grid is structured as follows:
%       A, B, C
%      D, E, F, G
%     H, I, J, K, L
%      M, N, O, P
%       Q, R, S
%
% The goal is to find an assignment of numbers to the variables A through S that
% satisfies all the sum constraints.
%
% Save this file as model.mzn. Download `csplib_023_magic_hexagon.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_023_magic_hexagon.json
%   minizinc model.mzn csplib_023_magic_hexagon_1.json

include "globals.mzn";

int: NUM_CELLS;                                  % the cells hold the numbers 1 to NUM_CELLS
int: MAGIC_SUM;                                  % the sum of each line
set of int: Numbers = 1..NUM_CELLS;             % the numbers the cells hold

var Numbers: A;
var Numbers: B;
var Numbers: C;
var Numbers: D;
var Numbers: E;
var Numbers: F;
var Numbers: G;
var Numbers: H;
var Numbers: I;
var Numbers: J;
var Numbers: K;
var Numbers: L;
var Numbers: M;
var Numbers: N;
var Numbers: O;
var Numbers: P;
var Numbers: Q;
var Numbers: R;
var Numbers: S;

array[Numbers] of var Numbers: LD = [A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S];

% the numbers are all different
constraint all_different(LD);

% the rows of the hexagon sum to the magic constant
constraint A + B + C = MAGIC_SUM;
constraint D + E + F + G = MAGIC_SUM;
constraint H + I + J + K + L = MAGIC_SUM;
constraint M + N + O + P = MAGIC_SUM;
constraint Q + R + S = MAGIC_SUM;

% the diagonals in one direction sum to the magic constant
constraint A + E + J + O + S = MAGIC_SUM;
constraint B + F + K + P = MAGIC_SUM;
constraint C + G + L = MAGIC_SUM;
constraint D + I + N + R = MAGIC_SUM;
constraint H + M + Q = MAGIC_SUM;

% the diagonals in the other direction sum to the magic constant
constraint A + D + H = MAGIC_SUM;
constraint B + E + I + M = MAGIC_SUM;
constraint C + F + J + N + Q = MAGIC_SUM;
constraint G + K + O + R = MAGIC_SUM;
constraint L + P + S = MAGIC_SUM;

solve satisfy;

output ["{\"LD\": ", showJSON(LD), "}"];
