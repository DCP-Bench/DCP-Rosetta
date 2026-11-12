% huey_dewey_louie: a clingo model from DCP Rosetta.
%
% Huey, Dewey and Louie are being questioned by their uncle, and make these statements: Huey says that
% Dewey and Louie have an equal share in it, so if one is guilty, so is the other. Dewey says that if
% Huey is guilty, then so is he. Louie says that Dewey and he are not both guilty. The three are cub
% scouts and cannot tell a lie, so each statement is true.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% a person is guilty (1) or not guilty (0)
guilty(0;1).

% each of the three is guilty or not
1 { huey(G) : guilty(G) } 1.
1 { dewey(G) : guilty(G) } 1.
1 { louie(G) : guilty(G) } 1.

% Huey: Dewey and Louie have an equal share, so if one is guilty, so is the other
:- dewey(A), louie(B), A != B.

% Dewey: if Huey is guilty, then so is Dewey
:- huey(1), dewey(0).

% Louie: Dewey and Louie are not both guilty
:- dewey(1), louie(1).

#show huey/1.
#show dewey/1.
#show louie/1.
