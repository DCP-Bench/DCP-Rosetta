% dinner: a MiniZinc model from DCP Rosetta.
%
% We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children. Grandparents cost
% $3 for dinner, parents $2 and children $0.50. There must be 20 total people at dinner and it must cost
% $20. How many grandparents, parents and children are going to dinner?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

% money in cents, so that all amounts are whole numbers
int: grandparent_cost = 300;                     % $3 per grandparent
int: parent_cost = 200;                          % $2 per parent
int: child_cost = 50;                            % $0.50 per child
int: total_people = 20;                          % the number of people at dinner
int: total_cost = 2000;                          % the cost of the dinner, $20

var 1..6: grandparents;                          % the number of grandparents going to dinner
var 1..10: parents;                              % the number of parents going to dinner
var 1..40: children;                             % the number of children going to dinner

% there are 20 people at dinner in total
constraint grandparents + parents + children = total_people;

% the dinner costs $20 in total
constraint grandparent_cost * grandparents + parent_cost * parents + child_cost * children = total_cost;

solve satisfy;
output ["{\"grandparents\": ", showJSON(grandparents), ", \"parents\": ", showJSON(parents),
        ", \"children\": ", showJSON(children), "}"];
