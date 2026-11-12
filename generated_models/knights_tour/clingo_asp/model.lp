% knights_tour: a clingo model from DCP Rosetta.
%
% A knight's tour is a sequence of moves of a knight on a chessboard such that the knight visits every square exactly once (without returning to the starting square). The objective is to find a knight's tour on a chessboard. The tour is represented by integers from 0 to n*n-1, where n is the size of the chessboard.
%
% Save this file as model.lp. Download `knights_tour.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py knights_tour.json
%   python -m clingo model.lp knights_tour_1.lp
%
% Input: n(N) holds the size N of the chessboard (indices are 0-based, as in the data).

index(0..N-1) :- n(N).
move(0..N*N-1) :- n(N).
square(R,C) :- index(R), index(C).

% each square gets exactly one move number
1 { x(R,C,V) : move(V) } 1 :- square(R,C).

% each move number is used on exactly one square
1 { x(R,C,V) : square(R,C) } 1 :- move(V).

% a knight jumps one square in one direction and two in the other
knight_jump(R,C,R2,C2) :- square(R,C), square(R2,C2), |R-R2| * |C-C2| == 2.

% the knight goes from the square of each move to a square a knight's jump away for the next move
1 { x(R2,C2,V+1) : knight_jump(R,C,R2,C2) } 1 :- x(R,C,V), move(V+1).

#show x/3.
