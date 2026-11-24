% discrete_tomography: a clingo model from DCP Rosetta.
%
% This is a little "tomography" problem, taken from an old issue of Scientific American. A matrix which contains
% zeroes and ones gets "x-rayed" vertically and horizontally, giving the total number of ones in each row and
% column. Reconstruct the contents of the matrix from this information.
%
% Save this file as model.lp. Download `discrete_tomography.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py discrete_tomography.json
%   python -m clingo model.lp discrete_tomography_1.lp

% Input: row_sums(I, S): the number of ones in row I is S; col_sums(J, S): the number of ones in column J is S
% (indices are 0-based, as in the data).

row(I) :- row_sums(I,_).
col(J) :- col_sums(J,_).

% each cell of the matrix is 0 or 1
1 { matrix(I,J,V) : V = 0..1 } 1 :- row(I), col(J).

% the number of ones in each row is the given sum
:- row_sums(I,S), #sum { V,J : matrix(I,J,V) } != S.

% the number of ones in each column is the given sum
:- col_sums(J,S), #sum { V,I : matrix(I,J,V) } != S.

#show matrix/3.
