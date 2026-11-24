% tsp: a MiniZinc model from DCP Rosetta.
%
% The travelling salesman problem, also known as the travelling salesperson problem (TSP), asks the
% following question: "Given a list of cities and the distances between each pair of cities (or the
% locations of the cities), what is the shortest possible route that visits each city exactly once and
% returns to the origin city?" The distance is defined as the Euclidean distance between the points
% rounded to an integer.
%
% Save this file as model.mzn. Download `tsp.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py tsp.json
%   minizinc model.mzn tsp_1.json

include "globals.mzn";

array[int, int] of int: locations;         % locations[c,1], locations[c,2]: the x and y coordinates of city c
set of int: Cities = index_set_1of2(locations);  % one index per city

% the Euclidean distance between two cities, rounded to an integer
function int: distance_between(int: a, int: b) =
    let {
        int: dx = locations[a,1] - locations[b,1];
        int: dy = locations[a,2] - locations[b,2];
    } in round(sqrt(int2float(dx * dx + dy * dy)));

array[Cities, Cities] of int: dist = array2d(Cities, Cities,
    [distance_between(i, j) | i in Cities, j in Cities]);

% succ[c]: the city visited right after city c
array[Cities] of var Cities: succ;

% the route visits each city exactly once and returns to its start, as one single circuit
constraint circuit(succ);

var int: travel_distance = sum(c in Cities)(dist[c, succ[c]]);  % the length of the route
var int: objective = travel_distance;

solve minimize objective;
output ["{\"travel_distance\": ", showJSON(travel_distance), "}"];
