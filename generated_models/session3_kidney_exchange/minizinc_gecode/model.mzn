% session3_kidney_exchange: a MiniZinc model from DCP Rosetta.
%
% At the hospital n people are on a waiting list for a kidney transplant. The compatibility between these
% people is a directed graph: compatible[i] is the set of people to which i can donate. Maximize the number of
% people that receive a new kidney: anyone who gives a kidney must receive one, and no person receives more
% than one kidney.
%
% Save this file as model.mzn. Download `session3_kidney_exchange.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session3_kidney_exchange.json
%   minizinc model.mzn session3_kidney_exchange_1.json

int: num_people;                                  % the number of people on the waiting list
% compatible[i, k]: the k-th person to whom person i can donate (rows padded with 0 to the longest row)
array[int, int] of int: compatible;
% compatible_len[i]: the number of real entries in row i of compatible (the reader's JSON has no such field)
array[int] of int: compatible_len;

set of int: Person = 1..num_people;               % one index per person
% can_donate_to[i]: the people to whom person i can donate, without the padding
array[Person] of set of int: can_donate_to =
  [{compatible[i, k] | k in 1..compatible_len[i]} | i in Person];

% transplants[i, j]: person i donates a kidney to person j
array[Person, Person] of var bool: transplants;

% a person can donate only to a person compatible with them
constraint forall(i, j in Person where not (j in can_donate_to[i]))(not transplants[i, j]);

% no person donates more than one kidney
constraint forall(i in Person)(sum(j in Person)(bool2int(transplants[i, j])) <= 1);

% no person receives more than one kidney
constraint forall(j in Person)(sum(i in Person)(bool2int(transplants[i, j])) <= 1);

% anyone who gives a kidney must receive one
constraint forall(i in Person)(
  exists(j in Person)(transplants[i, j]) -> exists(j in Person)(transplants[j, i])
);

% the number of people who receive a new kidney
var 0..num_people: objective = sum(i, j in Person)(bool2int(transplants[i, j]));

solve maximize objective;
output ["{\"transplants\": ", showJSON(transplants), "}"];
