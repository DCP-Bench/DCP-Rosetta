% five_statements: a MiniZinc model from DCP Rosetta.
%
% Determine which of the following statements is true.
% 1. Exactly one of these statements is false.
% 2. Exactly two of these statements are false.
% 3. Exactly three of these statements are false.
% 4. Exactly four of these statements are false.
% 5. Exactly five of these statements are false.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

set of int: Statements = 1..5;                   % statement i says exactly i statements are false

array[Statements] of var bool: statements;       % statements[i]: statement i is true
var int: false_count = sum(j in Statements)(bool2int(not statements[j]));  % how many are false

% statement 1 is true exactly when exactly one statement is false
constraint statements[1] <-> (false_count = 1);
% statement 2 is true exactly when exactly two statements are false
constraint statements[2] <-> (false_count = 2);
% statement 3 is true exactly when exactly three statements are false
constraint statements[3] <-> (false_count = 3);
% statement 4 is true exactly when exactly four statements are false
constraint statements[4] <-> (false_count = 4);
% statement 5 is true exactly when exactly five statements are false
constraint statements[5] <-> (false_count = 5);

solve satisfy;
output ["{\"statements\": ", showJSON(statements), "}"];
