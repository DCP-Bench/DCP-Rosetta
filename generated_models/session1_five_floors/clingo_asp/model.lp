% session1_five_floors: a clingo model from DCP Rosetta.
%
% Baker, Cooper, Fletcher, Miller and Smith live on the first five floors of an apartment house. Baker does not live on the fifth floor. Cooper does not live on the first floor. Fletcher does not live on either the fifth or the first floor. Miller lives on a higher floor than does Cooper. Smith does not live on a floor adjacent to Fletcher's. Fletcher does not live on a floor adjacent to Cooper's. They all live on different floors. Find the floors where these people live.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

floor(1..5).

% each person lives on exactly one of the five floors
1 { b(F) : floor(F) } 1.
1 { c(F) : floor(F) } 1.
1 { f(F) : floor(F) } 1.
1 { m(F) : floor(F) } 1.
1 { s(F) : floor(F) } 1.

lives(baker,F) :- b(F).
lives(cooper,F) :- c(F).
lives(fletcher,F) :- f(F).
lives(miller,F) :- m(F).
lives(smith,F) :- s(F).

% they all live on different floors
:- lives(X,F), lives(Y,F), X < Y.

% Baker does not live on the fifth floor
:- b(5).

% Cooper does not live on the first floor
:- c(1).

% Fletcher does not live on either the fifth or the first floor
:- f(5).
:- f(1).

% Miller lives on a higher floor than Cooper
:- m(M), c(C), M <= C.

% Smith does not live on a floor adjacent to Fletcher's
:- s(S), f(F), |S - F| == 1.

% Fletcher does not live on a floor adjacent to Cooper's
:- f(F), c(C), |F - C| == 1.

#show b/1.
#show c/1.
#show f/1.
#show m/1.
#show s/1.
