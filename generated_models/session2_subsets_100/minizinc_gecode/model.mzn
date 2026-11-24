% session2_subsets_100: a MiniZinc model from DCP Rosetta.
%
% Out of a set of integers, you are given a list of different integers. From this set A of integers you can
% always find two disjoint non-empty subsets, S and T, such that the sum of elements in S equals the sum of
% elements in T. S union T does not need to be all the elements of A. Find sets S and T for the given set A.
%
% Save this file as model.mzn. Download `session2_subsets_100.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session2_subsets_100.json
%   minizinc model.mzn session2_subsets_100_1.json

array[int] of int: A;                       % the given list of different integers

set of int: Elements = index_set(A);        % one index per element of A

array[Elements] of var bool: in_S;          % in_S[i]: element i is in S
array[Elements] of var bool: in_T;          % in_T[i]: element i is in T

% the sum of the elements of S equals the sum of the elements of T
constraint sum(i in Elements)(A[i] * bool2int(in_S[i]))
         = sum(i in Elements)(A[i] * bool2int(in_T[i]));

% S and T are disjoint
constraint forall(i in Elements)(not (in_S[i] /\ in_T[i]));

% S is non-empty
constraint sum(i in Elements)(bool2int(in_S[i])) > 0;

% T is non-empty
constraint sum(i in Elements)(bool2int(in_T[i])) > 0;

solve satisfy;
output ["{\"in_S\": ", showJSON(in_S), ", \"in_T\": ", showJSON(in_T), "}"];
