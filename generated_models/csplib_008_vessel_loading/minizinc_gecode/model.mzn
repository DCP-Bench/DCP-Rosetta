% csplib_008_vessel_loading: a MiniZinc model from DCP Rosetta.
%
% Supply vessels transport containers from site to site. The deck area is rectangular.
% Containers are cuboid and are laid out in a single layer, all positioned parallel to the
% sides of the deck. A container occupies the area from left to right across the width of the
% deck and from bottom to top along its length, with right - left and top - bottom being its
% width and length, in that order or rotated by 90 degrees. All of these lie between 0 and the
% size of the deck in that direction. Two containers may touch. The contents of the containers
% determine their class, and containers of certain classes must be separated by minimum
% distances, either along the deck or across it: separation[a, b] is the distance that
% containers of classes a and b must keep in at least one of the two directions. Decide whether
% the containers can be placed on the deck without overlapping and without violating any of the
% separation constraints.
%
% Save this file as model.mzn. Download `csplib_008_vessel_loading.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_008_vessel_loading.json
%   minizinc model.mzn csplib_008_vessel_loading_1.json

int: deck_width;                                     % the width of the deck
int: deck_length;                                    % the length of the deck
int: n_containers;                                   % the number of containers
set of int: Containers = 1..n_containers;            % one index per container
array[int] of int: width;                            % width[c]: width of container c
array[int] of int: length;                           % length[c]: length of container c
array[int] of int: classes;                          % classes[c]: class of container c
array[int, int] of int: separation;                  % separation[a, b]: distance classes a and b keep

% position of container c across the deck
array[Containers] of var 0..deck_width: left;
array[Containers] of var 0..deck_width: right;
% position of container c along the deck
array[Containers] of var 0..deck_length: bottom;
array[Containers] of var 0..deck_length: top;

% each container is placed in one of its two orientations
constraint forall(c in Containers)(
     (right[c] - left[c] = width[c] /\ top[c] - bottom[c] = length[c])
  \/ (right[c] - left[c] = length[c] /\ top[c] - bottom[c] = width[c])
);

% containers do not overlap and keep the separation their classes require in one direction
constraint forall(c, d in Containers where c < d)(
  let { int: sep = max(separation[classes[c], classes[d]], separation[classes[d], classes[c]]) } in
     right[c] + sep <= left[d]
  \/ left[c] >= right[d] + sep
  \/ top[c] + sep <= bottom[d]
  \/ bottom[c] >= top[d] + sep
);

solve satisfy;
output ["{\"left\": ", showJSON(left), ", \"right\": ", showJSON(right), ", \"top\": ", showJSON(top), ", \"bottom\": ", showJSON(bottom), "}"];
