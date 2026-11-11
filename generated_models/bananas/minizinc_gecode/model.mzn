% bananas: a MiniZinc model from DCP Rosetta.
%
% Five bananas cost three dollars, seven oranges cost five dollars, nine mangoes cost seven dollars, and
% three apples cost nine dollars. Buy 100 fruits for 100 dollars. All types of fruits need to be
% purchased, and the number of bananas and apples together should be as small as possible.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

int: total_fruits = 100;                  % the number of fruits to buy
int: total_dollars = 100;                 % the amount to spend, in dollars

% the number of each fruit bought, at least one of each kind (so at most total_fruits - 3 of any one kind)
var 1..total_fruits - 3: bananas;
var 1..total_fruits - 3: oranges;
var 1..total_fruits - 3: mangoes;
var 1..total_fruits - 3: apples;

% prices are in units of 1/315 dollar, since 315 is the least common multiple of 5, 7, 9 and 3:
% a banana costs 189, an orange 225, a mango 245 and an apple 945 units

% all the fruits bought come to 100 fruits
constraint bananas + oranges + mangoes + apples = total_fruits;

% the fruits bought come to exactly 100 dollars
constraint 189 * bananas + 225 * oranges + 245 * mangoes + 945 * apples = 315 * total_dollars;

var int: objective = bananas + apples;
solve minimize objective;
output ["{\"bananas\": ", showJSON(bananas), ", \"oranges\": ", showJSON(oranges),
        ", \"mangoes\": ", showJSON(mangoes), ", \"apples\": ", showJSON(apples), "}"];
