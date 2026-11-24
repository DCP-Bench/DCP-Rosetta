% ages_of_the_sons: a clingo model from DCP Rosetta.
%
% An old man asked a mathematician to guess the ages of his three sons. The old man said: "The product of their ages is 36." The mathematician said: "I need more information." The old man said: "Over there you can see a building. The sum of their ages equals the number of the windows in that building." After a short while the mathematician said: "I need more information." The old man said: "The oldest son has blue eyes." The mathematician said: "I got it." What are the ages of the three sons of the old man?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

age(1..36).

% tri(X,Y,Z): the ages X >= Y >= Z of three sons (positive integers, oldest first) multiply to 36
tri(X,Y,Z) :- age(X), age(Y), age(Z), X >= Y, Y >= Z, X*Y*Z == 36.

% the oldest son is unique in a triple: the oldest is strictly older than the second
uniqueOldest(X,Y,Z) :- tri(X,Y,Z), X > Y.

% the sum is not enough to know the ages: at least two different triples have that sum
ambiguous(S) :- tri(X1,Y1,Z1), tri(X2,Y2,Z2), t(X1,Y1,Z1) != t(X2,Y2,Z2), X1+Y1+Z1 == S, X2+Y2+Z2 == S.

% the sons' ages are one of the triples
1 { actual(X,Y,Z) : tri(X,Y,Z) } 1.

% the mathematician needed more information after the sum, so the sum is ambiguous
:- actual(X,Y,Z), not ambiguous(X+Y+Z).

% the mathematician got it after the blue eyes clue, so the oldest son of the actual triple is unique
:- actual(X,Y,Z), not uniqueOldest(X,Y,Z).

% the blue eyes clue settles it: no other triple with the same sum has a unique oldest son
:- actual(X,Y,Z), tri(X2,Y2,Z2), t(X,Y,Z) != t(X2,Y2,Z2), X+Y+Z == X2+Y2+Z2, uniqueOldest(X2,Y2,Z2).

a1(X) :- actual(X,_,_).
a2(Y) :- actual(_,Y,_).
a3(Z) :- actual(_,_,Z).

#show a1/1.
#show a2/1.
#show a3/1.
