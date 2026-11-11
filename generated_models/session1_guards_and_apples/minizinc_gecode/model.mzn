% session1_guards_and_apples: a MiniZinc model from DCP Rosetta.
%
% A boy wants to give an apple to a girl. To get to her, he has to pass through a number of gates, each with a guard. He
% bribes each guard with half of his apples, plus one. The boy does not have a knife, therefore he gives the guard an
% integer number of apples. After he's given the apple to the girl, he has no apples left, so he has exactly one apple after the last gate.
%
% Save this file as model.mzn. Download `session1_guards_and_apples.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session1_guards_and_apples.json
%   minizinc model.mzn session1_guards_and_apples_1.json

int: num_gates;                                % the number of gates, each with a guard

set of int: Positions = 1..num_gates + 1;      % position i: before gate i; the last one: after the last gate

% the most apples the boy can have at a position, working back from one apple after the last gate
int: max_apples = 3 * pow(2, num_gates) - 2;

array[Positions] of var 0..max_apples: apples; % apples[i]: apples the boy has at position i

% the boy gives each guard an integer number of apples, so his apples are even before each gate
constraint forall(i in 1..num_gates)(apples[i] mod 2 = 0);

% each guard gets half of the boy's apples plus one
constraint forall(i in 1..num_gates)(apples[i + 1] = apples[i] - (apples[i] div 2 + 1));

% after the last gate he has exactly one apple
constraint apples[num_gates + 1] = 1;

solve satisfy;
output ["{\"apples\": ", showJSON(apples), "}"];
