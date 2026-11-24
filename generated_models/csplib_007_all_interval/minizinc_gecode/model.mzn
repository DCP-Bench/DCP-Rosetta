% csplib_007_all_interval: a MiniZinc model from DCP Rosetta.
%
% Given n, find a vector s = (s_1, ..., s_n) such that s is a permutation of 0, 1, ..., n-1, and
% the interval vector v = (|s_2 - s_1|, |s_3 - s_2|, ..., |s_n - s_{n-1}|) is a permutation of
% 1, 2, ..., n-1. Such a series is an all-interval series of size n.
%
% Save this file as model.mzn. Download `csplib_007_all_interval.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_007_all_interval.json
%   minizinc model.mzn csplib_007_all_interval_1.json

include "globals.mzn";

int: n;                                 % the size of the series
set of int: Pitches = 0..n-1;           % the pitch classes
set of int: Steps = 1..n-1;             % the possible intervals
set of int: Positions = 1..n;           % one position per note
set of int: Gaps = 1..n-1;              % one interval per pair of neighbouring notes

array[Positions] of var Pitches: x;     % x[k]: pitch class at position k
array[Gaps] of var Steps: diffs;        % diffs[k]: interval between positions k and k+1

% the pitch classes form a permutation of 0..n-1
constraint all_different(x);

% the intervals form a permutation of 1..n-1
constraint all_different(diffs);

% each interval is the distance between the pitch classes of its two neighbours
constraint forall(k in Gaps)(diffs[k] = abs(x[k + 1] - x[k]));

solve satisfy;
output ["{\"x\": ", showJSON(x), ", \"diffs\": ", showJSON(diffs), "}"];
