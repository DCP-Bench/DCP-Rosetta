% cmo_2012: a clingo model from DCP Rosetta.
%
% Given two positive integers a and b, where a - b is a prime number p and a times b is a perfect square n^2,
% find the smallest value of a no less than a given minimum min_a. Also, b should be larger than 0, and none of
% the four values may exceed max_val.
%
% Save this file as model.lp. Download `cmo_2012.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py cmo_2012.json
%   python -m clingo model.lp cmo_2012_1.lp

% Input: min_a(L): a must be at least L; max_val(M): none of a, b, n and p may exceed M
% (indices are 0-based, as in the data).

% the primes below max_val: a number is composite when it is a product of two numbers from 2 to max_val
composite(X * Y) :- max_val(M), X = 2..M, Y = 2..M / X.
prime(P) :- max_val(M), P = 2..M - 1, not composite(P).

% candidate(N, B, A): n = N, b = B and a = A with a * b = n * n, where N is from 1 to max_val. Since a - b
% is positive, b is less than n; since a is at most max_val, b is at least n * n / max_val.
candidate(N, B, A) :- max_val(M), min_a(L), N = 1..M, B = (N * N + M - 1) / M..N - 1,
                      A = N * N / B, A * B == N * N, A >= L, A <= M, prime(A - B).

% exactly one candidate is picked, and the smallest a is wanted
1 { pick(N, B, A) : candidate(N, B, A) } 1.
#minimize { A, N, B : pick(N, B, A) }.

% the values of the picked candidate
a(A) :- pick(_, _, A).
b(B) :- pick(_, B, _).
n(N) :- pick(N, _, _).
p(A - B) :- pick(_, B, A).

#show a/1.
#show b/1.
#show n/1.
#show p/1.
