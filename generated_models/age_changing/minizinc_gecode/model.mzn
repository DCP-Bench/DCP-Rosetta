% age_changing: a MiniZinc model from DCP Rosetta.
%
% If you start with my age, in years, and apply the four operations +2, /8, -3 and *7 in some order,
% then the final answer you get is my husband's age. If you start with his age and apply the same four
% operations in a different order, then you get my age. Both ages are between 16 and 120, and every
% intermediate result is a positive integer, so a division by 8 must be exact. What are our two ages?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: min_age = 16;                              % the youngest age
int: max_age = 120;                             % the oldest age
int: max_value = 1000;                          % bound on every intermediate result (none reaches it)
set of int: Ops = 1..4;                         % the operations: 1 is +2, 2 is /8, 3 is -3, 4 is *7
set of int: Steps = 0..4;                       % the value before and after each of the four operations

var min_age..max_age: me;                       % my age
var min_age..max_age: husband;                  % my husband's age

% my_order[k]: the operation applied at step k, starting from my age
array[1..4] of var Ops: my_order;
% his_order[k]: the operation applied at step k, starting from his age
array[1..4] of var Ops: his_order;

% my_chain[k]: my value after k steps; my_chain[0] is my age
array[Steps] of var 1..max_value: my_chain;
% his_chain[k]: his value after k steps; his_chain[0] is his age
array[Steps] of var 1..max_value: his_chain;

% each operation is used exactly once, in my sequence
constraint all_different(my_order);
% each operation is used exactly once, in his sequence
constraint all_different(his_order);
% the two sequences are not the same order
constraint exists(k in 1..4)(my_order[k] != his_order[k]);

% starting from my age, the four operations give my husband's age
constraint my_chain[0] = me;
constraint my_chain[4] = husband;

% starting from his age, the four operations give my age
constraint his_chain[0] = husband;
constraint his_chain[4] = me;

% one step of the operation op: from old to new, exact division by 8 only
predicate step(var Ops: op, var int: old, var int: new) =
    (op = 1 -> new = old + 2)
    /\ (op = 2 -> 8 * new = old)
    /\ (op = 3 -> new = old - 3)
    /\ (op = 4 -> new = old * 7);

% each step of my sequence applies its operation
constraint forall(k in 1..4)(step(my_order[k], my_chain[k - 1], my_chain[k]));
% each step of his sequence applies its operation
constraint forall(k in 1..4)(step(his_order[k], his_chain[k - 1], his_chain[k]));

solve satisfy;

output ["{\"m\": ", showJSON(me), ", \"h\": ", showJSON(husband), "}"];
