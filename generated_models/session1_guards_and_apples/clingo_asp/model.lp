% session1_guards_and_apples: a clingo model from DCP Rosetta.
%
% A boy wants to give an apple to a girl. To get to her, he has to pass through a number of gates, each with a guard. He bribes each guard with half of his apples, plus one. The boy does not have a knife, therefore he gives the guard an integer number of apples. After he's given the apple to the girl, he has no apples left, so he has exactly one apple after the last gate.
%
% Save this file as model.lp. Download `session1_guards_and_apples.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session1_guards_and_apples.json
%   python -m clingo model.lp session1_guards_and_apples_1.lp

% Input: num_gates(G): the number of gates G the boy passes through; the gates are 0..G-1.
% Output: apples(I,V) holds the number V of apples the boy has before gate I, with I = G after the last gate.
gate(0..G-1) :- num_gates(G).

% after the last gate the boy has exactly one apple left, the one he gives to the girl
apples(G,1) :- num_gates(G).

% at each gate the guard takes half of the apples plus one, so with B apples left after the gate
% the boy had 2 * (B + 1) apples before it (the half is whole, since the number is even)
apples(I,2*(B+1)) :- gate(I), apples(I+1,B).

#show apples/2.
