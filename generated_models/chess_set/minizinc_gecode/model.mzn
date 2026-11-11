% chess_set: a MiniZinc model from DCP Rosetta.
%
% A small joinery makes two different sizes of boxwood chess sets. The small set requires 3 hours of
% machining on a lathe, and the large set requires 2 hours. There are four lathes with skilled operators
% who each work a 40 hour week, so there are 160 lathe-hours per week. The small chess set requires 1 kg of
% boxwood, and the large set requires 3 kg. Boxwood is scarce and only 200 kg per week can be obtained.
% When sold, each of the large chess sets yields a profit of $20, and each small chess set a profit of $5.
% Decide how many sets of each kind should be made each week so as to maximize profit.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

int: lathe_hours = 4 * 40;                   % lathe-hours available per week
int: boxwood_kg = 200;                       % kilograms of boxwood available per week
int: small_lathe_hours = 3;                  % lathe-hours for one small set
int: large_lathe_hours = 2;                  % lathe-hours for one large set
int: small_boxwood_kg = 1;                   % kilograms of boxwood for one small set
int: large_boxwood_kg = 3;                   % kilograms of boxwood for one large set
int: small_profit = 5;                       % profit from one small set, in dollars
int: large_profit = 20;                      % profit from one large set, in dollars

% small_set, large_set: the number of small and large sets made per week
var 0..boxwood_kg: small_set;
var 0..lathe_hours: large_set;

% the sets made use no more than the lathe-hours available
constraint small_lathe_hours * small_set + large_lathe_hours * large_set <= lathe_hours;

% the sets made use no more than the boxwood available
constraint small_boxwood_kg * small_set + large_boxwood_kg * large_set <= boxwood_kg;

% max_profit: the profit from the sets made, in dollars
var int: max_profit = small_profit * small_set + large_profit * large_set;
var int: objective = max_profit;

solve maximize objective;

output ["{\"small_set\": ", showJSON(small_set), ", \"large_set\": ", showJSON(large_set),
        ", \"max_profit\": ", showJSON(max_profit), "}"];
