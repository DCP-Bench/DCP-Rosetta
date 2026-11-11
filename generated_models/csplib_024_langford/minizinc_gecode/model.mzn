% csplib_024_langford: a MiniZinc model from DCP Rosetta.
%
% Consider two sets of the numbers from 1 to k. The problem is to arrange the 2k numbers in the two sets into a
% single sequence in which the two 1's appear one number apart, the two 2's appear two numbers apart, ..., and the
% two k's appear k numbers apart.
%
% Save this file as model.mzn. Download `csplib_024_langford.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_024_langford.json
%   minizinc model.mzn csplib_024_langford_1.json

include "globals.mzn";

int: k;                                          % the numbers are 1 to k, each appears twice
set of int: Numbers = 1..k;                      % the numbers in the two sets
set of int: Slots = 1..2 * k;                    % the positions in the sequence

% pos[i,1], pos[i,2]: the positions of the first and the second copy of number i
array[Numbers, 1..2] of var Slots: pos;
% sol[p]: the number at position p of the sequence
array[Slots] of var Numbers: sol;

% the 2k copies occupy the 2k different positions
constraint all_different([pos[i, j] | i in Numbers, j in 1..2]);

% the two copies of i are i + 1 positions apart, that is i numbers lie between them (the usual Langford reading)
constraint forall(i in Numbers)(pos[i, 2] - pos[i, 1] = i + 1);

% the sequence holds the number at each of the positions of its two copies
constraint forall(i in Numbers, j in 1..2)(sol[pos[i, j]] = i);

solve satisfy;

output ["{\"sol\": ", showJSON(sol), "}"];
