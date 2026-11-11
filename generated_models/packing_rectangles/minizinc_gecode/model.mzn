% packing_rectangles: a MiniZinc model from DCP Rosetta.
%
% The rectangular packing problem involves placing a set of rectangular items into a larger rectangular
% area such that no items overlap and all items are within the boundaries of the larger area. The
% objective is to minimize the total area of the larger rectangle required to pack all the items. Given
% the widths and heights of the items, determine their positions within the larger rectangle while
% ensuring no overlap and minimizing the total area.
%
% Save this file as model.mzn. Download `packing_rectangles.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py packing_rectangles.json
%   minizinc model.mzn packing_rectangles_1.json

include "globals.mzn";

array[int] of int: widths;               % widths[i]: width of item i
array[int] of int: heights;              % heights[i]: height of item i

set of int: Items = index_set(widths);

% total_x, total_y: width and height of the enclosing rectangle
var max(widths)..sum(widths): total_x;
var max(heights)..sum(heights): total_y;

% pos_x[i], pos_y[i]: lower-left corner of item i, counted from 0
array[Items] of var 0..sum(widths): pos_x;
array[Items] of var 0..sum(heights): pos_y;

% the total area of the enclosing rectangle, to be minimized
var int: objective = total_x * total_y;

% every item lies completely inside the enclosing rectangle
constraint forall(i in Items)(pos_x[i] + widths[i] <= total_x /\ pos_y[i] + heights[i] <= total_y);

% no two items overlap
constraint diffn(pos_x, pos_y, widths, heights);

solve minimize objective;

output ["{\"pos_x\": ", showJSON(pos_x), ", \"pos_y\": ", showJSON(pos_y),
        ", \"total_x\": ", showJSON(total_x), ", \"total_y\": ", showJSON(total_y), "}"];
