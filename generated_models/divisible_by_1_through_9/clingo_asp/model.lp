% Divisible by 1 through 9: find a ten-digit number that uses each digit 0 to 9 exactly
% once and where, for every n, the number formed by its first n digits is divisible by n.
% The statement fixes all the data (ten digits, divisors 1 to 10), so the instance has no
% facts.

% The positions of the number, 0 to 9 from left to right, and the digits 0 to 9.
position(0..9).
digit(0..9).

% digits(P, D): the digit at position P is D. Each position holds exactly one digit.
1 { digits(P, D) : digit(D) } 1 :- position(P).

% Each of the digits 0 to 9 is used exactly once.
:- digit(D), #count { P : digits(P, D) } != 1.

% The number formed by the first N digits is divisible by N.
% That number is the sum of D * 10**(N-1-P) over its positions P, which for N = 10 is
% above 2^31 - 1, the largest clingo integer. Replacing each place value 10**(N-1-P) by
% its remainder modulo N leaves the remainder of the sum modulo N unchanged and keeps the
% sum below 1000.
divisor(1..10).
:- divisor(N), S = #sum { D * ((10 ** (N - 1 - P)) \ N), P : digits(P, D), P < N }, S \ N != 0.

#show digits/2.
