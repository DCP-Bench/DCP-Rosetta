% csplib_006_golomb_rulers: a MiniZinc model from DCP Rosetta.
%
% A Golomb ruler is a set of m integers 0 = a_1 < a_2 < ... < a_m such that the m(m-1)/2
% differences a_j - a_i, for 1 <= i < j <= m, are all distinct. Such a ruler contains m marks
% and has length a_m. Find an optimal ruler, that is one of minimum length.
%
% Save this file as model.mzn. Download `csplib_006_golomb_rulers.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_006_golomb_rulers.json
%   minizinc model.mzn csplib_006_golomb_rulers_1.json

include "globals.mzn";

int: size;                                  % m, the number of marks
set of int: Marks = 1..size;                % one index per mark
int: max_length = size * size;              % a generous upper bound on the length

array[Marks] of var 0..max_length: marks;   % marks[k]: position of the k-th mark
var int: ruler_length = marks[size];        % the length is the position of the last mark

% the first mark is at position 0
constraint marks[1] = 0;

% the marks are in strictly increasing order
constraint forall(k in 1..size - 1)(marks[k] < marks[k + 1]);

% all differences between pairs of marks are distinct
constraint alldifferent([marks[j] - marks[i] | i in Marks, j in Marks where i < j]);

% redundant: the k gaps between marks k places apart are distinct positive integers
constraint forall(i in Marks, j in Marks where i < j)(marks[j] - marks[i] >= (j - i) * (j - i + 1) div 2);

var int: objective = ruler_length;
solve minimize objective;
output ["{\"marks\": ", showJSON(marks), ", \"length\": ", showJSON(ruler_length), "}"];
