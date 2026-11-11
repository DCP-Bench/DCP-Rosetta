% candies: a MiniZinc model from DCP Rosetta.
%
% Alice is a kindergarten teacher who wants to give candies to the children in her class. All the children
% sit in a line, and each of them has a rating score according to their usual performance. Alice wants to
% give at least 1 candy to each child. Children get jealous of their immediate neighbors, so if two children
% sit next to each other, then the one with the higher rating must get more candies. Alice wants to save
% money, so she wants to minimize the total number of candies.
%
% Save this file as model.mzn. Download `candies.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py candies.json
%   minizinc model.mzn candies_1.json

array[int] of int: ratings;                  % ratings[i]: the rating score of child i

set of int: Children = index_set(ratings);
int: n = card(Children);                     % the number of children

% x[i]: the number of candies given to child i, at least one each (at most n: an optimal solution never needs more, implied bound)
array[Children] of var 1..n: x;

% z: the total number of candies
var int: z = sum(x);
var int: objective = z;

% a child with a higher rating than the next child gets more candies than the next child
constraint forall(i in Children where i + 1 in Children)(
    ratings[i] > ratings[i + 1] -> x[i] > x[i + 1]
);

% a child with a lower rating than the next child gets fewer candies than the next child
constraint forall(i in Children where i + 1 in Children)(
    ratings[i] < ratings[i + 1] -> x[i] < x[i + 1]
);

solve minimize objective;

output ["{\"x\": ", showJSON(x), ", \"z\": ", showJSON(z), "}"];
