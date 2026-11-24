% session3_farmer_and_cows: a MiniZinc model from DCP Rosetta.
%
% A farmer has a number of cows, each numbered from 1 up to the total number of cows. Each cow gives a
% quantity of milk equal to its number. The farmer has a number of sons and wants to distribute his cows
% to them according to a given distribution: each son receives a given number of cows. The total quantity
% of milk produced should be the same for each son. How can he distribute the cows?
%
% Save this file as model.mzn. Download `session3_farmer_and_cows.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session3_farmer_and_cows.json
%   minizinc model.mzn session3_farmer_and_cows_1.json

include "globals.mzn";

int: num_cows;                                   % the number of cows, numbered 1..num_cows
int: num_sons;                                   % the number of sons
array[int] of int: cows_per_son;                 % cows_per_son[s]: the number of cows son s receives

set of int: Cows = 1..num_cows;                  % one index per cow
set of int: Sons = 1..num_sons;                  % one index per son (the output numbers sons from 0)
int: total_milk = sum(i in Cows)(i);             % the milk all the cows give together

% son[i]: the son cow i is given to
array[Cows] of var Sons: son;
% milk[s]: the total milk of the cows given to son s
array[Sons] of var 0..total_milk: milk;

% each son receives the number of cows the distribution gives him
constraint global_cardinality(son, Sons, [cows_per_son[s] | s in Sons]);

% the milk given to each son is the total of the cow numbers of the cows he receives
constraint bin_packing_load(milk, son, [i | i in Cows]);

% the milk of each son is the same: the total milk shared equally among the sons
constraint forall(s in Sons)(num_sons * milk[s] = total_milk);

% sons who receive the same number of cows are interchangeable: among each run of such sons, the one
% holding the lowest-numbered cow comes first (a symmetry break that does not change the problem)
constraint forall(s in 1..num_sons-1 where cows_per_son[s] = cows_per_son[s + 1])(
    forall(i in Cows)(son[i] = s + 1 -> exists(j in 1..i-1)(son[j] = s))
);

solve satisfy;
output ["{\"cow_assignments\": ", showJSON([son[i] - 1 | i in Cows]), "}"];
