% circular_table_averbach_1_2: a clingo model from DCP Rosetta.
%
% Three players (X, Y, Z) of different nationalities (American, English, French) are seated around a circular
% table playing a game of Hearts. Each passed three cards to the person on their right. Y passed three hearts to
% the American, X passed the queen of spades and two diamonds to the person who passed their cards to the
% Frenchwoman. Determine the nationality of each person.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% The seats are 0, 1 and 2, and seat 1 is right of seat 0, seat 2 right of seat 1, and seat 0 right of seat 2.
% The seat of each player, x(S), y(S) and z(S), is a different seat.
1 { x(S) : S = 0..2 } 1.
1 { y(S) : S = 0..2 } 1.
1 { z(S) : S = 0..2 } 1.
:- x(S), y(S).
:- x(S), z(S).
:- y(S), z(S).

% The seat of each nationality, american(S), english(S) and french(S), is a different seat. The same seat
% number in the player and nationality outputs denotes the same person.
1 { american(S) : S = 0..2 } 1.
1 { english(S) : S = 0..2 } 1.
1 { french(S) : S = 0..2 } 1.
:- american(S), english(S).
:- american(S), french(S).
:- english(S), french(S).

% Y passed three hearts to the American, who sits on the right of Y.
:- american(A), y(Y), A != (Y + 1) \ 3.

% X passed to the person who passed to the Frenchwoman, so the person on the right of X passed to her,
% and the Frenchwoman sits on the right of that person.
:- x(X), french(F), X != (F + 1) \ 3.

#show x/1.
#show y/1.
#show z/1.
#show american/1.
#show english/1.
#show french/1.
