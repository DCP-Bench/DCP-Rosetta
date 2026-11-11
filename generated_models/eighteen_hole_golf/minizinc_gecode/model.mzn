% eighteen_hole_golf: a MiniZinc model from DCP Rosetta.
%
% Generate an 18-hole golf course where each hole has a length of 3, 4, or 5, and the total length
% of the course is 72.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

set of int: Holes = 1..18;                  % the holes of the course
array[Holes] of var 3..5: holes;            % holes[h]: the length of hole h

% the total length of the course is 72
constraint sum(h in Holes)(holes[h]) = 72;

solve satisfy;
output ["{\"holes\": ", showJSON(holes), "}"];
