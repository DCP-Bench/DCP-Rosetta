% csplib_003_quasigroup_existence: a MiniZinc model from DCP Rosetta.
%
% An order m quasigroup is a Latin square of size m. That is, a m x m multiplication table in which each
% element occurs once in every row and column. A quasigroup can be specified by a set and a binary
% multiplication operator defined over this set. Quasigroup existence problems determine the existence
% or non-existence of quasigroups of a given size with additional properties. QG3.m problems are order m
% quasigroups for which (a*b)*(b*a) = a. We only consider the QG3.m problem for this task.
%
% Save this file as model.mzn. Download `csplib_003_quasigroup_existence.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_003_quasigroup_existence.json
%   minizinc model.mzn csplib_003_quasigroup_existence_1.json

include "globals.mzn";

int: m;                                  % the order of the quasigroup

set of int: Rows = 1..m;                 % one index per row and column
set of int: Elements = 0..m - 1;         % the elements of the quasigroup

% quasigroup[i, j]: the product of element i - 1 and element j - 1, an element from 0 to m - 1
array[Rows, Rows] of var Elements: quasigroup;

% every element occurs once in each row
constraint forall(i in Rows)(all_different([quasigroup[i, j] | j in Rows]));

% every element occurs once in each column
constraint forall(j in Rows)(all_different([quasigroup[i, j] | i in Rows]));

% (a*b)*(b*a) = a for all elements a and b
constraint forall(i, j in Rows)(quasigroup[quasigroup[i, j] + 1, quasigroup[j, i] + 1] = i - 1);

solve satisfy;

output ["{\"quasigroup\": ", showJSON(quasigroup), "}"];
