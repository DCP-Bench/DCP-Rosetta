% crossword: a clingo model from DCP Rosetta.
%
% We are to complete the crossword puzzle below. Given the list of words AFT, ALE, EEL, HEEL, HIKE, HOSES, KEEL,
% KNOT, LASER, LEE, LINE, SAILS, SHEET, STEER and TIE, select 8 words from the list, such that the puzzle can be completed.
%
%      1   2   3   4   5
%    +---+---+---+---+---+
%  1 | 1 |   | 2 |   | 3 |
%    +---+---+---+---+---+
%  2 | # | # |   | # |   |
%    +---+---+---+---+---+
%  3 | # | 4 |   | 5 |   |
%    +---+---+---+---+---+
%  4 | 6 | # | 7 |   |   |
%    +---+---+---+---+---+
%  5 | 8 |   |   |   |   |
%    +---+---+---+---+---+
%  6 |   | # | # |   | # |
%    +---+---+---+---+---+
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% The numbers 1 to 8 in the puzzle mark the words that start at those cells. Each word of the list is used at most once.

% The words, numbered in the order they are sorted by length, longest first, and then alphabetically:
% 0 HOSES, 1 LASER, 2 SAILS, 3 SHEET, 4 STEER, 5 HEEL, 6 HIKE, 7 KEEL, 8 KNOT, 9 LINE, 10 AFT, 11 ALE, 12 EEL,
% 13 LEE, 14 TIE. letter(W, K, C): the letter at position K (from 0) of word W is C.
letter(0,0,h). letter(0,1,o). letter(0,2,s). letter(0,3,e). letter(0,4,s).
letter(1,0,l). letter(1,1,a). letter(1,2,s). letter(1,3,e). letter(1,4,r).
letter(2,0,s). letter(2,1,a). letter(2,2,i). letter(2,3,l). letter(2,4,s).
letter(3,0,s). letter(3,1,h). letter(3,2,e). letter(3,3,e). letter(3,4,t).
letter(4,0,s). letter(4,1,t). letter(4,2,e). letter(4,3,e). letter(4,4,r).
letter(5,0,h). letter(5,1,e). letter(5,2,e). letter(5,3,l).
letter(6,0,h). letter(6,1,i). letter(6,2,k). letter(6,3,e).
letter(7,0,k). letter(7,1,e). letter(7,2,e). letter(7,3,l).
letter(8,0,k). letter(8,1,n). letter(8,2,o). letter(8,3,t).
letter(9,0,l). letter(9,1,i). letter(9,2,n). letter(9,3,e).
letter(10,0,a). letter(10,1,f). letter(10,2,t).
letter(11,0,a). letter(11,1,l). letter(11,2,e).
letter(12,0,e). letter(12,1,e). letter(12,2,l).
letter(13,0,l). letter(13,1,e). letter(13,2,e).
letter(14,0,t). letter(14,1,i). letter(14,2,e).

word(W) :- letter(W,_,_).
len(W,L) :- word(W), L = #count { K : letter(W,K,_) }.

% slot(N, L): the word that starts at the number N of the puzzle has L letters
slot(1,5). slot(2,5). slot(3,5). slot(4,4). slot(5,4). slot(6,3). slot(7,3). slot(8,5).

% cell(N, K, R, C): the letter K of the word at number N lies in row R and column C of the puzzle (from 0)
cell(1,K,0,K) :- K = 0..4.
cell(2,K,K,2) :- K = 0..4.
cell(3,K,K,4) :- K = 0..4.
cell(4,K,2,K+1) :- K = 0..3.
cell(5,K,K+2,3) :- K = 0..3.
cell(6,K,K+3,0) :- K = 0..2.
cell(7,K,3,K+2) :- K = 0..2.
cell(8,K,4,K) :- K = 0..4.

% pick(N, W): the word W is the word that starts at the number N
1 { pick(N,W) : len(W,L) } 1 :- slot(N,L).

% each word of the list is used at most once
:- pick(N,W), pick(M,W), N < M.

% the letters of two words that cross in a cell are the same letter
:- cell(N,K1,R,C), cell(M,K2,R,C), N < M, pick(N,W1), pick(M,W2),
   letter(W1,K1,X), not letter(W2,K2,X).

% e(I, W): the word W starts at the number I+1 of the puzzle, with the numbers counted from 0
e(N-1,W) :- pick(N,W).

#show e/2.
