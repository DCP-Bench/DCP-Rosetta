% csplib_014_solitaire_battleships: a clingo model from DCP Rosetta.
%
% The Battleships puzzle is played on a grid. The fleet consists of battleships (four squares long), cruisers (three
% squares long), destroyers (two squares long) and submarines (one square each). The ships lie horizontally or
% vertically, and no two ships occupy adjacent squares, not even diagonally. The numbers along the right side of the
% grid and below it give the number of squares in the corresponding rows and columns that are occupied by vessels.
% Some squares are given as hints. Find the grid in which each square is water, a submarine, or a ship part (left,
% right, top, bottom or middle).
%
% Save this file as model.lp. Download `csplib_014_solitaire_battleships.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_014_solitaire_battleships.json
%   python -m clingo model.lp csplib_014_solitaire_battleships_1.lp
%
% Input: rows(N), cols(N): the size of the grid; rowsum(R,V), colsum(C,V): the number V of ship squares in row R and
% column C; fleet_counts(I,0,L), fleet_counts(I,1,N): N ships of length L; hints(I,0,R), hints(I,1,C), hints(I,2,V):
% hint I fixes square (R,C) to the code V (indices are 0-based, as in the data).
% Codes: 0 water, 2 submarine, 3 left, 4 right, 5 top, 6 bottom, 7 middle. A middle square is written 8 when it
% lies in a horizontal ship and 9 when it lies in a vertical one; both are shown as 7.

row(0..N-1) :- rows(N).
col(0..N-1) :- cols(N).
cell(R,C) :- row(R), col(C).

% at(R,C,V): square (R,C) has code V
code(0;2;3;4;5;6;8;9).
1 { at(R,C,V) : code(V) } 1 :- cell(R,C).

% grid(R,C,V): the square (R,C) has code V in the answer, a middle square being 7
grid(R,C,V) :- at(R,C,V), V != 8, V != 9.
grid(R,C,7) :- at(R,C,8).
grid(R,C,7) :- at(R,C,9).

% shipcell(R,C): square (R,C) is a ship square, not water
shipcell(R,C) :- at(R,C,V), V != 0.

% the pieces of a ship point to their neighbours in the ship: a left piece to the east, a right piece to the west,
% a top piece to the south, a bottom piece to the north, and a middle piece to two opposite neighbours
east(R,C) :- at(R,C,3).
east(R,C) :- at(R,C,8).
west(R,C) :- at(R,C,4).
west(R,C) :- at(R,C,8).
south(R,C) :- at(R,C,5).
south(R,C) :- at(R,C,9).
north(R,C) :- at(R,C,6).
north(R,C) :- at(R,C,9).

% a piece points only to a square of the same ship, which points back to it
:- east(R,C), not west(R,C+1).
:- west(R,C), not east(R,C-1).
:- south(R,C), not north(R+1,C).
:- north(R,C), not south(R-1,C).

% ships do not touch: two ship squares side by side are in the same ship, and no two ship squares touch diagonally
:- shipcell(R,C), shipcell(R,C+1), not east(R,C).
:- shipcell(R,C), shipcell(R+1,C), not south(R,C).
:- shipcell(R,C), shipcell(R+1,C+1).
:- shipcell(R,C+1), shipcell(R+1,C).

% run(R,C,K): square (R,C) is the K-th square of a horizontal ship, counted from its left end
run(R,C,1) :- at(R,C,3).
run(R,C+1,K+1) :- run(R,C,K), east(R,C).
% vrun(R,C,K): square (R,C) is the K-th square of a vertical ship, counted from its top end
vrun(R,C,1) :- at(R,C,5).
vrun(R+1,C,K+1) :- vrun(R,C,K), south(R,C).

% ship(L,R,C): a ship of length L ends at square (R,C); a submarine is a ship of length 1
ship(K,R,C) :- run(R,C,K), at(R,C,4).
ship(K,R,C) :- vrun(R,C,K), at(R,C,6).
ship(1,R,C) :- at(R,C,2).

% the fleet has battleships, cruisers, destroyers and submarines, in the numbers given
:- ship(L,_,_), L > 4.
:- fleet_counts(I,0,L), fleet_counts(I,1,N), #count { R,C : ship(L,R,C) } != N.

% the number of ship squares in each row and each column
:- rowsum(R,N), #count { C : shipcell(R,C) } != N.
:- colsum(C,N), #count { R : shipcell(R,C) } != N.

% the hints are squares of the grid
hint(R,C,V) :- hints(I,0,R), hints(I,1,C), hints(I,2,V).
:- hint(R,C,V), not grid(R,C,V).

#show grid/3.
