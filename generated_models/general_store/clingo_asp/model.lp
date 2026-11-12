% general_store: a clingo model from DCP Rosetta.
%
% The owner of a general store, who is something of a puzzlist, has put up this sign to see if any of his
% mathematical friends can translate it properly. Each different letter stands for a different digit. The
% words above the horizontal line represent numbers that add to the total of 'ALL WOOL'. The problem is to
% change all the letters to the correct digits. Leading zeros are allowed: a word may start with the digit 0.
%
%        C H E S S
%  +       C A S H
%  +   B O W W O W
%  +     C H O P S
%  +   A L S O P S
%  + P A L E A L E
%  +       C O O L
%  +       B A S S
%  +       H O P S
%  +       A L E S
%  +       H O E S
%  +   A P P L E S
%  +       C O W S
%  +   C H E E S E
%  +   C H S O A P
%  +     S H E E P
%  _______________
%    A L L W O O L
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

letter(a;b;c;e;h;l;o;p;s;w).

% place(N, K, L): word N of the sign (numbered from the top, 1 to 16) has the letter L in its place K,
% where place 0 is the units place
place(1, 4, c).  place(1, 3, h).  place(1, 2, e).  place(1, 1, s).  place(1, 0, s).    % CHESS
place(2, 3, c).  place(2, 2, a).  place(2, 1, s).  place(2, 0, h).                    % CASH
place(3, 5, b).  place(3, 4, o).  place(3, 3, w).  place(3, 2, w).  place(3, 1, o).
place(3, 0, w).                                                                       % BOWWOW
place(4, 4, c).  place(4, 3, h).  place(4, 2, o).  place(4, 1, p).  place(4, 0, s).    % CHOPS
place(5, 5, a).  place(5, 4, l).  place(5, 3, s).  place(5, 2, o).  place(5, 1, p).
place(5, 0, s).                                                                       % ALSOPS
place(6, 6, p).  place(6, 5, a).  place(6, 4, l).  place(6, 3, e).  place(6, 2, a).
place(6, 1, l).  place(6, 0, e).                                                      % PALEALE
place(7, 3, c).  place(7, 2, o).  place(7, 1, o).  place(7, 0, l).                    % COOL
place(8, 3, b).  place(8, 2, a).  place(8, 1, s).  place(8, 0, s).                    % BASS
place(9, 3, h).  place(9, 2, o).  place(9, 1, p).  place(9, 0, s).                    % HOPS
place(10, 3, a). place(10, 2, l). place(10, 1, e). place(10, 0, s).                  % ALES
place(11, 3, h). place(11, 2, o). place(11, 1, e). place(11, 0, s).                  % HOES
place(12, 5, a). place(12, 4, p). place(12, 3, p). place(12, 2, l). place(12, 1, e).
place(12, 0, s).                                                                      % APPLES
place(13, 3, c). place(13, 2, o). place(13, 1, w). place(13, 0, s).                  % COWS
place(14, 5, c). place(14, 4, h). place(14, 3, e). place(14, 2, e). place(14, 1, s).
place(14, 0, e).                                                                      % CHEESE
place(15, 5, c). place(15, 4, h). place(15, 3, s). place(15, 2, o). place(15, 1, a).
place(15, 0, p).                                                                      % CHSOAP
place(16, 4, s). place(16, 3, h). place(16, 2, e). place(16, 1, e). place(16, 0, p).  % SHEEP

% total_letter(K, L): the total ALL WOOL has the letter L in its place K
total_letter(6, a). total_letter(5, l). total_letter(4, l). total_letter(3, w).
total_letter(2, o). total_letter(1, o). total_letter(0, l).                           % ALL WOOL

% each letter stands for exactly one digit
1 { digit(L, V) : V = 0..9 } 1 :- letter(L).

% each digit stands for at most one letter, so different letters stand for different digits
:- digit(L1, V), digit(L2, V), L1 < L2.

% the sixteen words add up to ALL WOOL: the value of the words (each letter's digit times its place value)
% minus the value of ALL WOOL is zero; the word number N and the place K keep equal terms apart
:- #sum { V * 10 ** K, N, K : place(N, K, L), digit(L, V);
          -V * 10 ** K, total, K : total_letter(K, L), digit(L, V) } != 0.

% the answer: the digit of each letter
a(V) :- digit(a, V).
b(V) :- digit(b, V).
c(V) :- digit(c, V).
e(V) :- digit(e, V).
h(V) :- digit(h, V).
l(V) :- digit(l, V).
o(V) :- digit(o, V).
p(V) :- digit(p, V).
s(V) :- digit(s, V).
w(V) :- digit(w, V).

#show a/1.
#show b/1.
#show c/1.
#show e/1.
#show h/1.
#show l/1.
#show o/1.
#show p/1.
#show s/1.
#show w/1.
