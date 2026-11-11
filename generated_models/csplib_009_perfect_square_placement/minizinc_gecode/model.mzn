% csplib_009_perfect_square_placement: a MiniZinc model from DCP Rosetta.
%
% The perfect square placement problem (also called the squared square problem) is to pack a set
% of squares with given integer sizes into a bigger square, such that no squares overlap each other
% and all square borders are parallel to the border of the big square. The sum of the square
% surfaces is equal to the surface of the packing square, so there is no spare capacity.
%
% Save this file as model.mzn. Download `csplib_009_perfect_square_placement.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_009_perfect_square_placement.json
%   minizinc model.mzn csplib_009_perfect_square_placement_1.json

include "globals.mzn";

int: base;                                     % the side length of the big square
array[int] of int: sides;                      % sides[i]: the side length of square i
set of int: Squares = index_set(sides);        % one index per square
set of int: Units = 0..base - 1;               % the unit cells along one side, counted from 0

% (x_coords[i], y_coords[i]): the lower-left corner of square i
array[Squares] of var 0..base: x_coords;
array[Squares] of var 0..base: y_coords;

% every square lies inside the big square
constraint forall(i in Squares)(x_coords[i] + sides[i] <= base);
constraint forall(i in Squares)(y_coords[i] + sides[i] <= base);

% no two squares overlap
constraint diffn(x_coords, y_coords, sides, sides);

% the squares cover the big square exactly: their surfaces add up to its surface
constraint sum(i in Squares)(sides[i] * sides[i]) = base * base;

% redundant: the squares crossing each column of the big square fill its height
constraint forall(c in Units)(
    sum(i in Squares)(sides[i] * bool2int(x_coords[i] <= c /\ c < x_coords[i] + sides[i])) = base);

% redundant: the squares crossing each row of the big square fill its width
constraint forall(r in Units)(
    sum(i in Squares)(sides[i] * bool2int(y_coords[i] <= r /\ r < y_coords[i] + sides[i])) = base);

solve satisfy;
output ["{\"x_coords\": ", showJSON(x_coords), ", \"y_coords\": ", showJSON(y_coords), "}"];
