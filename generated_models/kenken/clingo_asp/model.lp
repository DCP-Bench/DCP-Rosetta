% kenken: a clingo model from DCP Rosetta.
%
% KenKen or KEN-KEN is a style of arithmetic and logical puzzle sharing several characteristics with sudoku.
% The objective is to fill the grid in with the digits 1 through 6 such that each row contains exactly one of
% each digit, each column contains exactly one of each digit, and each group of cells (a cage) achieves its
% specified result using a mathematical operation (addition, subtraction, multiplication or division), where
% digits may repeat within a group. In this problem the operations are not given: each cage is its result and
% its cells. A cage of one cell holds its result. A cage of two cells may use any of the four operations, and a
% division must be exact. A larger cage uses either addition or multiplication.
%
% Save this file as model.lp. Download `kenken.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py kenken.json
%   python -m clingo model.lp kenken_1.lp
%
% Input: n(N) holds the size N of the grid. problem(I, 0, T) holds the target T of cage I (0-based), and
% problem(I, 1, K, 0, R) and problem(I, 1, K, 1, C) hold the row R and column C of the K-th cell of cage I
% (the indices I and K count from 0, the rows and columns count from 1, as in the data).

digit(1..N) :- n(N).
index(0..N-1) :- n(N).

% x(R, C, V): the cell in row R and column C (counted from 0) holds the digit V
% every cell holds exactly one digit
1 { x(R,C,V) : digit(V) } 1 :- index(R), index(C).

% each row holds each digit exactly once
1 { x(R,C,V) : index(C) } 1 :- index(R), digit(V).

% each column holds each digit exactly once
1 { x(R,C,V) : index(R) } 1 :- index(C), digit(V).

% target(I, T): cage I has the target T; size(I, S): cage I has S cells
target(I,T) :- problem(I,0,T).
size(I,S) :- target(I,_), S = #count { K : problem(I,1,K,0,_) }.

% val(I, K, V): the K-th cell of cage I holds the digit V
val(I,K,V) :- problem(I,1,K,0,R), problem(I,1,K,1,C), x(R - 1,C - 1,V).

% total(I, S): the digits of cage I add up to S
total(I,S) :- target(I,_), S = #sum { V,K : val(I,K,V) }.

% product(I, K, P): the first K+1 digits of cage I multiply to P, so the last one is the product of the cage
% (clingo's aggregates have no product)
product(I,0,V) :- val(I,0,V).
product(I,K + 1,P * V) :- product(I,K,P), val(I,K + 1,V).
cage_product(I,P) :- size(I,S), product(I,S - 1,P).

% a cage of two cells reaches its target by the sum, product, difference or quotient of its two digits A and B,
% in either order (a division must be exact)
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), A + B == T.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), A * B == T.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), A - B == T.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), B - A == T.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), A * T == B.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), B * T == A.

% a cage of any other size (one cell, or three or more) reaches its target by the sum or the product of its digits
reached(I) :- size(I,S), S != 2, target(I,T), total(I,T).
reached(I) :- size(I,S), S != 2, target(I,T), cage_product(I,T).

% every cage reaches its target
:- target(I,_), not reached(I).

#show x/3.
