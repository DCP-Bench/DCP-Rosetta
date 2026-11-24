% session1_bank_card: a MiniZinc model from DCP Rosetta.
%
% My bank card has a 4 digit pin, abcd. I use the following facts to help me remember it:
%
% - no two digits are the same
% - the 2-digit number cd is 3 times the 2-digit number ab
% - the 2-digit number da is 2 times the 2-digit number bc
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

var 0..9: a;   % the first digit of the pin
var 0..9: b;   % the second digit of the pin
var 0..9: c;   % the third digit of the pin
var 0..9: d;   % the fourth digit of the pin

% no two digits are the same
constraint all_different([a, b, c, d]);

% the 2-digit number cd is 3 times the 2-digit number ab
constraint 10 * c + d = 3 * (10 * a + b);

% the 2-digit number da is 2 times the 2-digit number bc
constraint 10 * d + a = 2 * (10 * b + c);

solve satisfy;
output ["{\"a\": ", showJSON(a), ", \"b\": ", showJSON(b), ", \"c\": ", showJSON(c), ", \"d\": ", showJSON(d), "}"];
