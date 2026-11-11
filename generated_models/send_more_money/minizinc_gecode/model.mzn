% send_more_money: a MiniZinc model from DCP Rosetta.
%
% The "Send More Money" puzzle is a classic cryptarithmetic problem where each letter represents a unique digit. The
% goal is to assign digits to the letters such that the following equation holds true:
%
%    SEND
%   + MORE
%   ------
%    MONEY
%
% Each letter must be assigned a unique digit from 0 to 9, and the first letter of each word cannot be zero.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

var 0..9: s;   % the digit of S
var 0..9: e;   % the digit of E
var 0..9: n;   % the digit of N
var 0..9: d;   % the digit of D
var 0..9: m;   % the digit of M
var 0..9: o;   % the digit of O
var 0..9: r;   % the digit of R
var 0..9: y;   % the digit of Y

% each letter represents a unique digit
constraint all_different([s, e, n, d, m, o, r, y]);

% the first letter of SEND is not zero
constraint s != 0;

% the first letter of MORE is not zero
constraint m != 0;

% SEND + MORE = MONEY
constraint 1000*s + 100*e + 10*n + d + 1000*m + 100*o + 10*r + e = 10000*m + 1000*o + 100*n + 10*e + y;

solve satisfy;
output ["{\"d\": ", showJSON(d), ", \"e\": ", showJSON(e), ", \"m\": ", showJSON(m), ", \"n\": ", showJSON(n),
        ", \"o\": ", showJSON(o), ", \"r\": ", showJSON(r), ", \"s\": ", showJSON(s), ", \"y\": ", showJSON(y), "}"];
