% isbn: a MiniZinc model from DCP Rosetta.
%
% An ISBN-13 is a 13-digit number whose last digit is a check digit calculated from the first 12
% digits: multiply the first 12 digits alternately by 1 and 3 (starting with 1), sum the products,
% and the check digit is (10 - (sum % 10)) % 10. Given a list of 13 integers representing an ISBN-13,
% where -1 represents an unknown digit, find the values of the unknown digits such that the resulting
% number is a valid ISBN-13. An ISBN-13 must start with 978 or 979.
%
% Save this file as model.mzn. Download `isbn.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py isbn.json
%   minizinc model.mzn isbn_1.json

array[int] of int: isbn_init;                    % the given digits, -1 marks an unknown digit

set of int: Digits = index_set(isbn_init);       % positions 1..13 of the ISBN
int: n = length(isbn_init);                      % the number of digits, 13

% isbn[i]: digit i of the ISBN
array[Digits] of var 0..9: isbn;

% the given digits are kept
constraint forall(i in Digits where isbn_init[i] != -1)(isbn[i] = isbn_init[i]);

% the ISBN starts with 978 or 979
constraint isbn[1] = 9 /\ isbn[2] = 7 /\ (isbn[3] = 8 \/ isbn[3] = 9);

% the last digit is the check digit of the first 12 digits, weighted 1, 3, 1, 3, ...
constraint isbn[n] = (10 - (sum(i in 1..n - 1)(isbn[i] * (if i mod 2 = 1 then 1 else 3 endif)) mod 10)) mod 10;

solve satisfy;

output ["{\"isbn\": ", showJSON(isbn), "}"];
