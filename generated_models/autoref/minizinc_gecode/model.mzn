% autoref: a MiniZinc model from DCP Rosetta.
%
% Given an integer n > 0 and an integer m >= 0, find a non-empty finite series S = (s0, s1, ..., sn, sn+1)
% of integers between 0 and n such that (1) there are si occurrences of i in S for each integer i from 0
% to n, and (2) sn+1 = m.
%
% Save this file as model.mzn. Download `autoref.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py autoref.json
%   minizinc model.mzn autoref_1.json

include "globals.mzn";

int: n;                                  % the largest value in the series
int: m;                                  % the required value of the last element

set of int: Values = 0..n;               % the values an element of the series can take
set of int: Positions = 0..n+1;          % the positions of the series

array[Positions] of var Values: s;       % s[k]: the k-th element of the series

% the last element of the series is m
constraint s[n+1] = m;

% the value i occurs in the series exactly s[i] times, for every i from 0 to n
constraint forall(i in Values)(count(s, i) = s[i]);

solve satisfy;
output ["{\"s\": ", showJSON(s), "}"];
