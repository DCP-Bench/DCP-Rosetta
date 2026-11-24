% big_bang2: a clingo model from DCP Rosetta.
%
% Nontransitive dice: find a set of five dice such that the dominance relationships between the dice are isomorphic to the corresponding relationships in the game Rock-Paper-Scissors extended by the choices Lizard and Spock. Each choice beats two other choices and is beaten by two other choices. The ten beats relationships are: Rock crushes Scissors and Lizard; Paper covers Rock and disproves Spock; Scissors cuts Paper and decapitates Lizard; Lizard eats Paper and poisons Spock; Spock vaporizes Rock and smashes Scissors. Each die has six integer-valued faces, and each face value must be between 1 and 12 inclusive. Face values may repeat, both within a die and across dice. A die A beats a die B when A has a strictly larger face value than B in more than half of all possible pairs of faces.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the dice, numbered 0 to 4: 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock
die(0..4).

% the faces of each die, numbered 0 to 5, and the face values 1 to 12
face(0..5).
value(1..12).

% each face of each die has exactly one value
1 { dice(D, F, V) : value(V) } 1 :- die(D), face(F).

% the die A beats the die B when A has a larger face value than B in more than half of the 36 pairs of faces
beats(A, B) :- die(A), die(B), A != B, #count { F, G : dice(A, F, X), dice(B, G, Y), X > Y } > 18.

% the beats relationships of the game, as (winner, loser) pairs
:- wins(A, B), not beats(A, B).
wins(0,2). wins(0,3). wins(1,0). wins(1,4). wins(2,1). wins(2,3). wins(3,1). wins(3,4). wins(4,0). wins(4,2).

#show dice/3.
