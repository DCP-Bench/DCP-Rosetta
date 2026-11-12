% dinner: a clingo model from DCP Rosetta.
%
% We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children. Grandparents cost $3
% for dinner, parents $2 and children $0.50. There must be 20 total people at dinner and it must cost $20.
% How many grandparents, parents and children are going to dinner?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% one number of grandparents, of parents and of children
1 { grandparents(G) : G = 1..6 } 1.
1 { parents(P) : P = 1..10 } 1.
1 { children(C) : C = 1..40 } 1.

% there must be 20 people at dinner
:- grandparents(G), parents(P), children(C), G + P + C != 20.

% the dinner must cost $20, counted in cents: $3 is 300 cents, $2 is 200 cents and $0.50 is 50 cents
:- grandparents(G), parents(P), children(C), 300*G + 200*P + 50*C != 2000.

#show grandparents/1.
#show parents/1.
#show children/1.
