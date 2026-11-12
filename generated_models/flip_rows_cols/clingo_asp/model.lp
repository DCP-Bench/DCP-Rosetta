% flip_rows_cols: a clingo model from DCP Rosetta.
%
% Given is an array of positive and negative numbers. You can flip the sign of entire rows and columns,
% as many of them as you like. The goal is to make each one of all the rows and columns sum to positive
% numbers (or zero), and then to find the solution that has the smallest overall sum.
%
% Save this file as model.lp. Download `flip_rows_cols.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py flip_rows_cols.json
%   python -m clingo model.lp flip_rows_cols_1.lp
%
% Input: input_matrix(I, J, V) holds the value V in row I and column J (indices are 0-based, as in the data).

sign(-1;1).

% the rows and the columns are those that have a value
row(I) :- input_matrix(I, _, _).
col(J) :- input_matrix(_, J, _).

% each row is flipped (-1) or not (1)
1 { row_signs(I, S) : sign(S) } 1 :- row(I).

% each column is flipped (-1) or not (1)
1 { col_signs(J, S) : sign(S) } 1 :- col(J).

% the value of each cell once its row and its column are flipped
cell(I, J, V * RS * CS) :- input_matrix(I, J, V), row_signs(I, RS), col_signs(J, CS).

% every row sums to a positive number or zero
:- row(I), #sum { X, J : cell(I, J, X) } < 0.

% every column sums to a positive number or zero
:- col(J), #sum { X, I : cell(I, J, X) } < 0.

% the overall sum is minimized
#minimize { X, I, J : cell(I, J, X) }.

#show row_signs/2.
#show col_signs/2.
