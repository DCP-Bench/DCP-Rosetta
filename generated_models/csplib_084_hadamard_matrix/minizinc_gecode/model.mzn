% csplib_084_hadamard_matrix: a MiniZinc model from DCP Rosetta.
%
% Hadamard matrix Legendre pairs: find two sequences a and b of l values, each -1 or +1, such that the
% sum of their periodic autocorrelation functions equals -2 at every shift s = 1..m, where m = (l-1)/2,
% the entries of a sum to 1 and the entries of b sum to 1. The periodic autocorrelation at shift s
% wraps around the sequence, so position i + s is taken mod l. The length l is odd.
%
% Save this file as model.mzn. Download `csplib_084_hadamard_matrix.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_084_hadamard_matrix.json
%   minizinc model.mzn csplib_084_hadamard_matrix_1.json

int: l;                                          % the length of each sequence (odd)

set of int: Pos = 1..l;                          % the positions of a sequence
set of int: Shifts = 1..(l - 1) div 2;           % the shifts s = 1..m, m = (l-1)/2

array[Pos] of var {-1, 1}: a;                    % the entries of the first sequence
array[Pos] of var {-1, 1}: b;                    % the entries of the second sequence

% the entries of a sum to 1
constraint sum(i in Pos)(a[i]) = 1;

% the entries of b sum to 1
constraint sum(i in Pos)(b[i]) = 1;

% for every shift s, the periodic autocorrelations of a and b sum to -2
constraint forall(s in Shifts)(
    sum(i in Pos)(a[i] * a[(i + s - 1) mod l + 1] + b[i] * b[(i + s - 1) mod l + 1]) = -2
);

solve satisfy;
output ["{\"a\": ", showJSON(a), ", \"b\": ", showJSON(b), "}"];
