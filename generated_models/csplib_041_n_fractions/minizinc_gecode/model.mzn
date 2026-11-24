% csplib_041_n_fractions: a MiniZinc model from DCP Rosetta.
%
% Find distinct non-zero digits such that the following equation holds: A / BC + D / EF + G / HI = 1
% Here, BC, EF, and HI are two-digit numbers formed by B and C, E and F, and H and I, respectively.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

var 1..9: A;                                      % the non-zero digits A to I
var 1..9: B;
var 1..9: C;
var 1..9: D;
var 1..9: E;
var 1..9: F;
var 1..9: G;
var 1..9: H;
var 1..9: I;

% the digits A to I are all different
constraint all_different([A, B, C, D, E, F, G, H, I]);

var 11..99: BC = 10 * B + C;                      % the two-digit number BC
var 11..99: EF = 10 * E + F;                      % the two-digit number EF
var 11..99: HI = 10 * H + I;                      % the two-digit number HI

% A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI to avoid fractions
constraint A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI;

solve satisfy;

output ["{\"A\": ", showJSON(A), ", \"B\": ", showJSON(B), ", \"C\": ", showJSON(C), ", \"D\": ", showJSON(D),
        ", \"E\": ", showJSON(E), ", \"F\": ", showJSON(F), ", \"G\": ", showJSON(G), ", \"H\": ", showJSON(H),
        ", \"I\": ", showJSON(I), "}"];
