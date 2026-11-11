% csplib_049_number_partitioning: a MiniZinc model from DCP Rosetta.
%
% This problem consists of finding a partition of the numbers 1..N into two sets A and B such that A and B
% have the same cardinality, the sum of the numbers in A equals the sum of the numbers in B, and the sum of
% the squares of the numbers in A equals the sum of the squares of the numbers in B. There is no solution
% for N < 8.
%
% Save this file as model.mzn. Download `csplib_049_number_partitioning.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_049_number_partitioning.json
%   minizinc model.mzn csplib_049_number_partitioning_1.json

include "globals.mzn";

int: n;                                         % N: the numbers 1..N are partitioned

set of int: Numbers = 1..n;                      % the numbers to partition
set of int: Half = 1..n div 2;                   % the positions of set A and of set B

array[Half] of var Numbers: A;                   % A[k]: the k-th number of set A
array[Half] of var Numbers: B;                   % B[k]: the k-th number of set B

% A and B have the same cardinality and together hold all N numbers, so N is even
constraint n mod 2 = 0;

% every number is in exactly one of A and B
constraint all_different(A ++ B);

% the sum of the numbers in A equals the sum of the numbers in B
constraint sum(A) = sum(B);

% the sum of the squares of the numbers in A equals the sum of the squares of the numbers in B
constraint sum(k in Half)(A[k] * A[k]) = sum(k in Half)(B[k] * B[k]);

solve satisfy;
output ["{\"A\": ", showJSON(A), ", \"B\": ", showJSON(B), "}"];
