% csplib_021_crossfigures: a clingo model from DCP Rosetta.
%
% Crossfigures are the numerical equivalent of crosswords. You have a grid and some clues with numerical answers to place on this grid. Clues come in several different forms (for example: Across 1. 25 across times two, 2. five dozen, 5. a square number, 10. prime, 14. 29 across times 21 down ...). The grid is:
%
%   1  2  _  3  X  4  _  5  6    1
%   7  _  X  8  _  _  X  9  _    2
%   _  X  10 _  X  11 12 X  _    3
%   13 14 _  _  X  15 _  16 _    4
%   X  _  X  X  X  X  X  _  X    5
%   17 _  18 19 X  20 21 _ 22    6
%   _  X  23 _  X  24 _  X  _    7
%   25 26 X  27 _  _  X  28 _    8
%   29 _  _  _  X  30 _  _  _    9
%
% The clues are: Across 1 27 across times two; 4 4 down plus seventy-one; 7 18 down plus four; 8 6 down divided by sixteen; 9 2 down minus eighteen; 10 dozen in six gross; 11 5 down minus seventy; 13 26 down times 23 across; 15 6 down minus 350; 17 25 across times 23 across; 20 a square number; 23 a prime number; 24 a square number; 25 20 across divided by seventeen; 27 6 down divided by four; 28 four dozen; 29 seven gross; 30 22 down plus 450. Down 1 1 across plus twenty-seven; 2 five dozen; 3 30 across plus 888; 4 two times 17 across; 5 29 across divided by twelve; 6 28 across times 23 across; 10 10 across plus four; 12 three times 24 across; 14 13 across divided by sixteen; 16 28 down times fifteen; 17 13 across minus 399; 18 29 across divided by eighteen; 19 22 down minus ninety-four; 20 20 across minus nine; 21 25 across minus fifty-two; 22 20 down times six; 26 five times 24 across; 28 21 down plus twenty-seven.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% ---- The grid: black cells, counted from row 0 and column 0 ----
black(0,4).
black(1,(2;6)).
black(2,(1;4;7)).
black(3,4).
black(4,(0;2;3;4;5;6;8)).
black(5,4).
black(6,(1;4;7)).
black(7,(2;6)).
black(8,4).

% word(W, Len, Row, Col): word W has Len digits and starts in row Row, column Col (counted from 1,
% as in the diagram). Across words run right, down words run down.
word(across(1),4,1,1).   word(across(4),4,1,6).   word(across(7),2,2,1).   word(across(8),3,2,4).
word(across(9),2,2,8).   word(across(10),2,3,3).  word(across(11),2,3,6).  word(across(13),4,4,1).
word(across(15),4,4,6).  word(across(17),4,6,1).  word(across(20),4,6,6).  word(across(23),2,7,3).
word(across(24),2,7,6).  word(across(25),2,8,1).  word(across(27),3,8,4).  word(across(28),2,8,8).
word(across(29),4,9,1).  word(across(30),4,9,6).
word(down(1),4,1,1).     word(down(2),2,1,2).     word(down(3),4,1,4).     word(down(4),4,1,6).
word(down(5),2,1,8).     word(down(6),4,1,9).     word(down(10),2,3,3).    word(down(12),2,3,7).
word(down(14),3,4,2).    word(down(16),3,4,8).    word(down(17),4,6,1).    word(down(18),2,6,3).
word(down(19),4,6,4).    word(down(20),4,6,6).    word(down(21),2,6,7).    word(down(22),4,6,9).
word(down(26),2,8,2).    word(down(28),2,8,8).

% spot(W, I, R, C): digit I of word W (0 is the most significant) sits in cell (R, C)
spot(across(N),I,R-1,C-1+I) :- word(across(N),L,R,C), I = 0..L-1.
spot(down(N),I,R-1+I,C-1)   :- word(down(N),L,R,C),   I = 0..L-1.

% ---- The numbers ----
% value(W, V): the number written in word W is V. A word of L digits takes a value below 10^L, and its
% digits are the L digits of V (a leading digit 0 is allowed, as the statement allows a digit 0).
% The numbers are the decision variables; the digits follow from them.
1 { value(W,V) : V = 0..10**L-1 } 1 :- word(W,L,_,_).

% digit(W, I, D): digit I of word W is D
digit(W,I,D) :- value(W,V), word(W,L,_,_), I = 0..L-1, D = (V / 10**(L-1-I)) \ 10.

% two words that cross share a cell, so they write the same digit there
:- spot(W1,I1,R,C), spot(W2,I2,R,C), W1 < W2, digit(W1,I1,D), not digit(W2,I2,D).

% the digit in each white cell is that of the word through it; black cells hold 0
m(R,C,D) :- spot(W,I,R,C), digit(W,I,D).
m(R,C,0) :- black(R,C).

% ---- The clues ----
% is(W, V): the clue gives the number of W outright
:- is(W,V), not value(W,V).

% lin(X, K, Y, C): the number of X is K times the number of Y plus C. A division in a clue such as
% "6 down divided by 16" is written the other way round, as "8 across times 16"
:- lin(X,K,Y,C), value(X,VX), (VX - C) \ K != 0.
:- lin(X,K,Y,C), value(X,VX), not value(Y,(VX - C) / K).

% prod(X, Y, Z): the number of X is the product of the numbers of Y and Z
:- prod(X,Y,Z), value(Y,VY), value(Z,VZ), not value(X,VY * VZ).

% square(W) and prime(W): the number of W is a square number, or a prime number
:- square(W), value(W,V), not is_square(V).
:- prime(W), value(W,V), not is_prime(V).

% the square numbers and the primes of at most four digits
is_square(I*I) :- I = 1..100.
is_composite(X*Y) :- X = 2..99, Y = X..9999 / X.
is_prime(N) :- N = 2..9999, not is_composite(N).

% Across clues
lin(across(1), 2, across(27), 0).        % 1: 27 across times two
lin(across(4), 1, down(4), 71).          % 4: 4 down plus seventy-one
lin(across(7), 1, down(18), 4).          % 7: 18 down plus four
lin(down(6), 16, across(8), 0).          % 8: 6 down divided by sixteen
lin(across(9), 1, down(2), -18).         % 9: 2 down minus eighteen
is(across(10), (6 * 144) / 12).          % 10: a dozen in six gross
lin(across(11), 1, down(5), -70).        % 11: 5 down minus seventy
prod(across(13), down(26), across(23)).  % 13: 26 down times 23 across
lin(across(15), 1, down(6), -350).       % 15: 6 down minus 350
prod(across(17), across(25), across(23)).% 17: 25 across times 23 across
square(across(20)).                      % 20: a square number
prime(across(23)).                       % 23: a prime number
square(across(24)).                      % 24: a square number
lin(across(20), 17, across(25), 0).      % 25: 20 across divided by seventeen
lin(down(6), 4, across(27), 0).          % 27: 6 down divided by four
is(across(28), 4 * 12).                  % 28: four dozen
is(across(29), 7 * 144).                 % 29: seven gross
lin(across(30), 1, down(22), 450).       % 30: 22 down plus 450

% Down clues
lin(down(1), 1, across(1), 27).          % 1: 1 across plus twenty-seven
is(down(2), 5 * 12).                     % 2: five dozen
lin(down(3), 1, across(30), 888).        % 3: 30 across plus 888
lin(down(4), 2, across(17), 0).          % 4: two times 17 across
lin(across(29), 12, down(5), 0).         % 5: 29 across divided by twelve
prod(down(6), across(28), across(23)).   % 6: 28 across times 23 across
lin(down(10), 1, across(10), 4).         % 10: 10 across plus four
lin(down(12), 3, across(24), 0).         % 12: three times 24 across
lin(across(13), 16, down(14), 0).        % 14: 13 across divided by sixteen
lin(down(16), 15, down(28), 0).          % 16: 28 down times fifteen
lin(down(17), 1, across(13), -399).      % 17: 13 across minus 399
lin(across(29), 18, down(18), 0).        % 18: 29 across divided by eighteen
lin(down(19), 1, down(22), -94).         % 19: 22 down minus ninety-four
lin(down(20), 1, across(20), -9).        % 20: 20 across minus nine
lin(down(21), 1, across(25), -52).       % 21: 25 across minus fifty-two
lin(down(22), 6, down(20), 0).           % 22: 20 down times six
lin(down(26), 5, across(24), 0).         % 26: five times 24 across
lin(down(28), 1, down(21), 27).          % 28: 21 down plus twenty-seven

#show m/3.
