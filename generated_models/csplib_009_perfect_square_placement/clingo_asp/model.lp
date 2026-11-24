% csplib_009_perfect_square_placement: a clingo model from DCP Rosetta.
%
% Pack a set of squares with given integer sizes into a bigger square so that no two squares overlap and all square
% borders are parallel to the border of the big square. The sum of the areas of the squares equals the area of the
% big square, so there is no spare capacity. Find the position of every square.
%
% Save this file as model.lp. Download `csplib_009_perfect_square_placement.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_009_perfect_square_placement.json
%   python -m clingo model.lp csplib_009_perfect_square_placement_1.lp
%
% Input: base(B): the side B of the big square; sides(I,S): the side S of square I (indices are 0-based, as in the data).

square(I) :- sides(I,_).

% x_coords(I,X), y_coords(I,Y): the lower left corner of square I is at column X and row Y
1 { x_coords(I,X) : X = 0..B-S } 1 :- sides(I,S), base(B).
1 { y_coords(I,Y) : Y = 0..B-S } 1 :- sides(I,S), base(B).

% apart(I,J): square I lies to the left of square J, or below it, so that the two do not overlap
apart(I,J) :- x_coords(I,X), sides(I,S), x_coords(J,X2), X + S <= X2.
apart(I,J) :- y_coords(I,Y), sides(I,S), y_coords(J,Y2), Y + S <= Y2.

% no two squares overlap
:- square(I), square(J), I < J, not apart(I,J), not apart(J,I).

#show x_coords/2.
#show y_coords/2.
