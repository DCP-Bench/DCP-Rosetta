% abbots_puzzle: a MiniZinc model from DCP Rosetta.
%
% If 100 bushels of corn were distributed among 100 people such that each man received three bushels,
% each woman two, and each child half a bushel, and there are five times as many women as men, find the
% number of men, women, and children.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

var 0..100: men;                         % the number of men
var 0..100: women;                       % the number of women
var 0..100: children;                    % the number of children

% the 100 people are men, women and children
constraint men + women + children = 100;

% the 100 bushels are shared out: 3 per man, 2 per woman, half a bushel per child
% (doubled, so that half bushels stay integers)
constraint 6 * men + 4 * women + children = 200;

% there are five times as many women as men
constraint women = 5 * men;

solve satisfy;

output ["{\"children\": ", showJSON(children), ", \"men\": ", showJSON(men),
        ", \"women\": ", showJSON(women), "}"];
