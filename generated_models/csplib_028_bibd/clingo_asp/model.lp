% csplib_028_bibd: a clingo model from DCP Rosetta.
%
% Balanced Incomplete Block Design (BIBD) generation is a standard combinatorial problem from design theory. A BIBD is defined as an arrangement of v distinct objects into b blocks such that each block contains exactly k distinct objects, each object occurs in exactly r different blocks, and every two distinct objects occur together in exactly lambda blocks. Another way of defining a BIBD is in terms of its incidence matrix, which is a v by b binary matrix with exactly r ones per row, k ones per column, and with a scalar product of lambda between any pair of distinct rows. A BIBD is therefore specified by its parameters (v, b, r, k, lambda).
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
% Save this file as model.lp. Download `csplib_028_bibd.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_028_bibd.json
%   python -m clingo model.lp csplib_028_bibd_1.lp

% Input: v(V): the number of objects; b(B): the number of blocks; r(R): the number of blocks each object
% is in; k(K): the number of objects in each block; l(L): the number of blocks two objects share.
% The objects are numbered 0..v-1 and the blocks 0..b-1.

object(0..V-1) :- v(V).
block(0..B-1) :- b(B).

% matrix(I,J,1) when object I is in block J, and matrix(I,J,0) otherwise
{ matrix(I,J,1) } :- object(I), block(J).
matrix(I,J,0) :- object(I), block(J), not matrix(I,J,1).

% each object occurs in exactly r blocks
:- object(I), r(R), #count { J : matrix(I,J,1) } != R.

% each block contains exactly k objects
:- block(J), k(K), #count { I : matrix(I,J,1) } != K.

% every two distinct objects occur together in exactly lambda blocks
:- object(I1), object(I2), I1 < I2, l(L), #count { J : matrix(I1,J,1), matrix(I2,J,1) } != L.

#show matrix/3.
