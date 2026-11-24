% giant_cat_army: a MiniZinc model from DCP Rosetta.
%
% Start with the list [0] and build the list by one of three operations: adding 5, adding 7, or taking
% the square root. The game is complete when the list contains 2, 10 and 14 in that order, and there
% can be other numbers between them. All the elements are distinct, they are all at most 60, and they
% are all integers. Find a sequence of 24 integers that starts from 0, ends with 14, and satisfies
% these conditions.
%
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: n = 24;                                  % the number of entries in the list
set of int: Entries = 1..n;                   % positions in the list
set of int: Values = 0..60;                   % the values an entry may take

% x[i]: the i-th entry of the list
array[Entries] of var Values: x;

% the entries are all distinct
constraint all_different(x);

% the list starts from 0 and ends with 14
constraint x[1] = 0;
constraint x[n] = 14;

% each entry comes from the one before it by adding 5, adding 7, or taking the square root: the
% entry before a square root is the square of the entry after it
constraint forall(i in 1..n-1)(x[i+1] = x[i] + 5 \/ x[i+1] = x[i] + 7 \/ x[i] = x[i+1] * x[i+1]);

% the list contains 2, then later 10, then later 14 (the last entry)
constraint exists(i, j in Entries where i < j /\ j < n)(x[i] = 2 /\ x[j] = 10);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
