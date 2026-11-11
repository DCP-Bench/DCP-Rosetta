% crypta: a MiniZinc model from DCP Rosetta.
%
% Cryptarithmetic puzzle: the addition below holds, where all letters are distinct digits
% from 0 to 9, and the first letter of each number cannot be zero.
%
%     B A I J J A J I I A H F C F E B B J E A
%   + D H F G A B C D I D B I F F A G F E J E
%   -----------------------------------------
%   = G J E G A C D D H F A F J B F I H E E F
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

% the digit each letter stands for
var 0..9: A;
var 0..9: B;
var 0..9: C;
var 0..9: D;
var 0..9: E;
var 0..9: F;
var 0..9: G;
var 0..9: H;
var 0..9: I;
var 0..9: J;

% the letters of the first number, the second number and the sum, column by column,
% from the leftmost column 1 to the rightmost column 20
array[1..20] of var 0..9: first = [B, A, I, J, J, A, J, I, I, A, H, F, C, F, E, B, B, J, E, A];
array[1..20] of var 0..9: second = [D, H, F, G, A, B, C, D, I, D, B, I, F, F, A, G, F, E, J, E];
array[1..20] of var 0..9: total = [G, J, E, G, A, C, D, D, H, F, A, F, J, B, F, I, H, E, E, F];

% carry[k]: the carry from column k+1 into column k (0 or 1)
array[0..20] of var 0..1: carry;

% no carry enters the rightmost column, and none leaves the leftmost column
constraint carry[20] = 0;
constraint carry[0] = 0;

% each column adds up: its two digits and the carry from the right make its sum digit
% and a carry to the left
constraint forall(k in 1..20)(first[k] + second[k] + carry[k] = total[k] + 10 * carry[k - 1]);

% different letters stand for different digits
constraint all_different([A, B, C, D, E, F, G, H, I, J]);

% the first letter of each number cannot be zero
constraint B > 0;
constraint D > 0;
constraint G > 0;

solve satisfy;

output ["{\"A\": ", showJSON(A), ", \"B\": ", showJSON(B), ", \"C\": ", showJSON(C),
        ", \"D\": ", showJSON(D), ", \"E\": ", showJSON(E), ", \"F\": ", showJSON(F),
        ", \"G\": ", showJSON(G), ", \"H\": ", showJSON(H), ", \"I\": ", showJSON(I),
        ", \"J\": ", showJSON(J), "}"];
