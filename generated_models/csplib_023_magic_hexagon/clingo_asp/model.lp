% csplib_023_magic_hexagon: a clingo model from DCP Rosetta.
%
% A magic hexagon problem involves arranging the numbers 1 to 19 in a hexagonal pattern such that the sum of the numbers in each of the 15 lines (rows and diagonals) is equal to a magic constant, which is 38. The hexagonal grid is structured as a hexagon of rows of 3, 4, 5, 4 and 3 cells, with the cells lettered A to S from the top row downwards. The goal is to find an assignment of numbers to the variables A through S that satisfies all the sum constraints.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
% Save this file as model.lp. Download `csplib_023_magic_hexagon.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_023_magic_hexagon.json
%   python -m clingo model.lp csplib_023_magic_hexagon_1.lp

% Input: nUM_CELLS(N): the number N of cells (19); mAGIC_SUM(S): the magic sum S of each line (38).
% The first letter of each field name is lowered, as the converter does.

cell(0..N-1) :- nUM_CELLS(N).
number(1..N) :- nUM_CELLS(N).

% The cells are numbered 0 to 18 from A to S: the top row is 0 1 2, then 3 4 5 6, 7 8 9 10 11,
% 12 13 14 15, and the bottom row is 16 17 18.
% line(L, C): cell C lies on line L. Lines 0 to 4 are the five rows; lines 5 to 9 run down and to the
% right; lines 10 to 14 run down and to the left.
line(0,(0;1;2)).
line(1,(3;4;5;6)).
line(2,(7;8;9;10;11)).
line(3,(12;13;14;15)).
line(4,(16;17;18)).
line(5,(0;3;7)).
line(6,(1;4;8;12)).
line(7,(2;5;9;13;16)).
line(8,(6;10;14;17)).
line(9,(11;15;18)).
line(10,(2;6;11)).
line(11,(1;5;10;15)).
line(12,(0;4;9;14;18)).
line(13,(3;8;13;17)).
line(14,(7;12;16)).

% each cell holds exactly one number
1 { lD(C,V) : number(V) } 1 :- cell(C).

% each number is used in one cell only
:- lD(C1,V), lD(C2,V), C1 < C2.

% every line adds up to the magic sum
:- mAGIC_SUM(S), line(L,_), S != #sum { V,C : line(L,C), lD(C,V) }.

#show lD/2.
