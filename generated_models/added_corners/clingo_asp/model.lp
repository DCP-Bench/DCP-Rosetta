% added_corners: a clingo model from DCP Rosetta.
%
% Enter the digits 1 through 8 into the eight positions around the edge of a 3 by 3 grid whose centre is empty, using each digit exactly once. The corners are circles (C) and the middles of the sides are squares (F): the top row is C F C, the middle row is F and F with the centre empty, and the bottom row is C F C. The number in each square must equal the sum of the numbers in the two circles adjoining it.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% The digits to place are 1 to 8, and the edge positions are 0 to 7 in reading order:
% 0 1 2 / 3 _ 4 / 5 6 7 (so the squares are 1, 3, 4 and 6, and the circles 0, 2, 5 and 7).
digit(1..8).
slot(0..7).

% each position holds exactly one digit
1 { positions(I,D) : digit(D) } 1 :- slot(I).

% each digit is used exactly once
1 { positions(I,D) : slot(I) } 1 :- digit(D).

% the top middle square (1) is the sum of the top left (0) and top right (2) circles
:- positions(1,B), positions(0,A), positions(2,C), B != A + C.

% the left middle square (3) is the sum of the top left (0) and bottom left (5) circles
:- positions(3,D), positions(0,A), positions(5,F), D != A + F.

% the right middle square (4) is the sum of the top right (2) and bottom right (7) circles
:- positions(4,E), positions(2,C), positions(7,H), E != C + H.

% the bottom middle square (6) is the sum of the bottom left (5) and bottom right (7) circles
:- positions(6,G), positions(5,F), positions(7,H), G != F + H.

#show positions/2.
