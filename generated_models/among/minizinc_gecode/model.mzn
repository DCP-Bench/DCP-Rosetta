% among: a MiniZinc model from DCP Rosetta.
%
% Find an array x of n integers between 0 and 7, inclusive, such that exactly m of them take one of the
% values in v. The other elements may take any other value in that range.
%
% Save this file as model.mzn. Download `among.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py among.json
%   minizinc model.mzn among_1.json

include "globals.mzn";

int: n;                                        % the number of elements of x
int: m;                                        % the number of elements of x that take a value in v
array[int] of int: v;                          % the values that count

set of int: Positions = 1..n;
set of int: Values = 0..7;

array[Positions] of var Values: x;

% exactly m elements of x take one of the values in v
constraint among(m, x, array2set(v));

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
