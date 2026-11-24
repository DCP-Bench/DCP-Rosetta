% csplib_005_autocorrelation: a MiniZinc model from DCP Rosetta.
%
% These problems have many practical applications in communications and electrical engineering. The
% objective is to construct a binary sequence of length n that minimizes the autocorrelations between
% bits. Each bit in the sequence takes the value +1 or -1. With periodic (or cyclic) boundary conditions,
% the k-th autocorrelation C_k is the sum over i from 0 to n-1 of S_i * S_((i+k) mod n). This problem uses
% the periodic ones: the aim is to minimize the sum of their squares, E = sum over k from 1 to n-1 of C_k^2.
%
% Save this file as model.mzn. Download `csplib_005_autocorrelation.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_005_autocorrelation.json
%   minizinc model.mzn csplib_005_autocorrelation_1.json

int: n;                                   % the length of the sequence

set of int: Positions = 1..n;             % one index per bit of the sequence
set of int: Lags = 1..n - 1;              % the autocorrelations C_k, for k from 1 to n-1

% sequence[i]: the bit at position i, +1 or -1 (the position i here is i - 1 in the problem)
array[Positions] of var {-1, 1}: sequence;

% C[k]: the k-th periodic autocorrelation of the sequence
array[Lags] of var -n..n: C;

% each autocorrelation is the sum of products of bits k apart, wrapping around at the end
constraint forall(k in Lags)(
    C[k] = sum(i in Positions)(sequence[i] * sequence[((i + k - 1) mod n) + 1]));

% E: the sum of the squares of the autocorrelations
var int: objective = sum(k in Lags)(C[k] * C[k]);

solve minimize objective;

output ["{\"sequence\": ", showJSON(sequence), "}"];
