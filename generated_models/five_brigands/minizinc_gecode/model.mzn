% five_brigands: a MiniZinc model from DCP Rosetta.
%
% The five Spanish brigands, Alfonso, Benito, Carlos, Diego, and Esteban, were counting their spoils
% after a raid, when it was found that they had captured altogether exactly 200 doubloons. One of the
% band pointed out that if Alfonso had twelve times as much, Benito three times as much, Carlos the
% same amount, Diego half as much, and Esteban one-third as much, they would still have altogether
% just 200 doubloons. How many doubloons had each? Also, no brigand had less than one doubloon.
%
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

int: total = 200;                          % the doubloons captured, and the reweighted total

var 1..total: A;                           % the doubloons of Alfonso
var 1..total: B;                           % the doubloons of Benito
var 1..total: C;                           % the doubloons of Carlos
var 1..total: D;                           % the doubloons of Diego
var 1..total: E;                           % the doubloons of Esteban

% the brigands together have exactly 200 doubloons
constraint A + B + C + D + E = total;
% reweighted (12A + 3B + C + D/2 + E/3), the total is still 200; multiplied by 6 to clear fractions
constraint 72 * A + 18 * B + 6 * C + 3 * D + 2 * E = 6 * total;

solve satisfy;
output ["{\"A\": ", showJSON(A), ", \"B\": ", showJSON(B), ", \"C\": ", showJSON(C),
        ", \"D\": ", showJSON(D), ", \"E\": ", showJSON(E), "}"];
