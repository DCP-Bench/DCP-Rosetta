% circling_squares: a MiniZinc model from DCP Rosetta.
%
% Place a different whole number in each of ten squares around a circle, so that the sum of the squares of
% any two adjacent numbers equals the sum of the squares of the two numbers diametrically opposite them.
% Fractions are not allowed, and no number needs more than two figures. The numbers A = 16, B = 2, F = 8
% and G = 14 are given.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

% the ten squares, in order around the circle
int: max_value = 99;              % no number needs more than two figures
set of int: Figures = 0..max_value;
var Figures: A;
var Figures: B;
var Figures: C;
var Figures: D;
var Figures: E;
var Figures: F;
var Figures: G;
var Figures: H;
var Figures: I;
var Figures: K;

int: num_squares = 10;               % the squares in the circle
array[1..num_squares] of var int: circle = [A, B, C, D, E, F, G, H, I, K];

function var int: sq(var int: v) = v * v;

% each square holds a different number
constraint all_different(circle);

% the given numbers
constraint A = 16 /\ B = 2 /\ F = 8 /\ G = 14;

% for each pair of adjacent squares, the sum of their squares equals the sum of the squares of the
% two squares diametrically opposite them (indices wrap around the circle)
constraint forall(i in 1..num_squares)(
    sq(circle[i]) + sq(circle[i mod num_squares + 1]) =
    sq(circle[(i + 4) mod num_squares + 1]) + sq(circle[(i + 5) mod num_squares + 1])
);

solve satisfy;

output [
    "{\"A\": ", showJSON(A), ", \"B\": ", showJSON(B), ", \"C\": ", showJSON(C),
    ", \"D\": ", showJSON(D), ", \"E\": ", showJSON(E), ", \"F\": ", showJSON(F),
    ", \"G\": ", showJSON(G), ", \"H\": ", showJSON(H), ", \"I\": ", showJSON(I),
    ", \"K\": ", showJSON(K), "}"
];
