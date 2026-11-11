% cmo_2012: a MiniZinc model from DCP Rosetta.
%
% Given two positive integers a and b, where a - b is a prime number p and a * b is a perfect square n^2,
% find the smallest value of a no less than a given minimum min_a. Also, b should be larger than 0, and
% none of the four values may exceed max_val.
%
% Save this file as model.mzn. Download `cmo_2012.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py cmo_2012.json
%   minizinc model.mzn cmo_2012_1.json

int: min_a;                                  % the smallest allowed value of a
int: max_val;                                % the largest allowed value of a, b, n and p

% a prime p <= max_val has no divisor above the square root of max_val, so only divisors up to this are tested
int: root_bound = ceil(sqrt(int2float(max_val)));

% t: the search variable. If a - b = p is prime and a * b is a square, then a = (t + 1)^2, b = t^2,
% n = t * (t + 1) and p = 2t + 1 for some t >= 1, so the search runs over t.
var 1..max_val: t;
var int: a = (t + 1) * (t + 1);
var int: b = t * t;
var int: n = t * (t + 1);
var int: p = 2 * t + 1;

var int: objective = a;

% a is no less than the given minimum
constraint a >= min_a;

% a does not exceed the bound
constraint a <= max_val;

% b is larger than 0 and does not exceed the bound
constraint b > 0 /\ b <= max_val;

% n does not exceed the bound
constraint n <= max_val;

% p does not exceed the bound
constraint p <= max_val;

% the difference a - b is the prime number p
constraint a - b = p;

% p is prime: no integer from 2 up to the square root bound, below p, divides it
constraint forall(d in 2..root_bound)(d < p -> p mod d != 0);

% the product a * b is the perfect square n^2
constraint a * b = n * n;

solve minimize objective;

output ["{\"a\": ", showJSON(a), ", \"b\": ", showJSON(b), ", \"n\": ", showJSON(n),
        ", \"p\": ", showJSON(p), "}"];
