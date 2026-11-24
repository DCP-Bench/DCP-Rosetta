% five_statements: a clingo model from DCP Rosetta.
%
% Determine which of the following statements is true. Exactly one of these statements is false. Exactly two of these statements are false. Exactly three of these statements are false. Exactly four of these statements are false. Exactly five of these statements are false.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the statements are numbered 0..4, and statement I says that exactly I+1 statements are false
statement(0..4).

% each statement is true (truth(I)) or false
{ truth(I) : statement(I) }.

% the number of false statements
falses(N) :- N = #count { J : statement(J), not truth(J) }.

% a true statement I says that exactly I+1 statements are false
:- truth(I), falses(N), N != I + 1.

% a false statement I says something untrue: the number of false statements is not I+1
:- statement(I), not truth(I), falses(I+1).

% the output: each statement as true or false
statements(I, true) :- truth(I).
statements(I, false) :- statement(I), not truth(I).

#show statements/2.
