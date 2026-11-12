% calvin_puzzle: a clingo model from DCP Rosetta.
%
% Take an n by n grid, representing n^2 squares, and completely fill every square with the numbers 1 to n^2
% in sequence, each used once, starting from any square, based on two types of movements. Movement type I:
% if the next number is placed vertically or horizontally, it must be placed exactly three squares away from
% the previous number (a two square gap between them). Movement type II: if the next number is placed
% diagonally, it must be placed exactly two squares away from the previous number (a one square gap between them).
%
% Save this file as model.lp. Download `calvin_puzzle.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py calvin_puzzle.json
%   python -m clingo model.lp calvin_puzzle_1.lp

% Input: n(N) gives the side N of the grid (indices are 0-based, as in the data).

cell(0..N-1, 0..N-1) :- n(N).
number(1..N*N) :- n(N).

% move(I,J,A,B): the square (A,B) is reached from the square (I,J) by a movement of type I
% (vertically or horizontally, three squares away) or of type II (diagonally, two squares away)
move(I,J,A,B) :- cell(I,J), cell(A,B), |A-I| == 3, B == J.
move(I,J,A,B) :- cell(I,J), cell(A,B), |B-J| == 3, A == I.
move(I,J,A,B) :- cell(I,J), cell(A,B), |A-I| == 2, |B-J| == 2.

% at(K,I,J): the number K is in the square (I,J)
% each number is in exactly one square
1 { at(K,I,J) : cell(I,J) } 1 :- number(K).
% each square holds exactly one number
1 { at(K,I,J) : number(K) } 1 :- cell(I,J).

% the number after K is placed by a movement from the square of K
:- at(K,I,J), number(K+1), not 1 { at(K+1,A,B) : move(I,J,A,B) }.

% x(I,J,K): the square (I,J) holds the number K
x(I,J,K) :- at(K,I,J).

#show x/3.
