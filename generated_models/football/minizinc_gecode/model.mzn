% football: a MiniZinc model from DCP Rosetta.
%
% A chairman gives an upper limit of GBP 30 million on the purchase of players. Buy players so that
% their total price is as close to that limit as possible without going over. The players come in four
% groups, each with a price in GBP millions: goalkeepers, defenders, midfielders and strikers. You must
% buy exactly one goalkeeper, at least two defenders, at least three midfielders and at least two
% strikers, and at least eleven players in total.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: budget = 30000;                                 % the upper limit on spending, in GBP thousands
array[1..26] of int: price = [                       % price of each player, in GBP thousands
    730, 1280, 3880,                                 % goalkeepers g1-g3
    920, 1310, 1620, 2410, 2790, 3280, 3910, 4570,   % defenders d1-d8
    1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130,  % midfielders m1-m10
    4460, 6470, 7780, 8390, 9500];                   % strikers s1-s5
set of int: Players = index_set(price);
set of int: Goalkeepers = 1..3;
set of int: Defenders = 4..11;
set of int: Midfielders = 12..21;
set of int: Strikers = 22..26;

% buy[p]: player p is bought
array[Players] of var bool: buy;

% buy exactly one goalkeeper
constraint sum(p in Goalkeepers)(bool2int(buy[p])) = 1;

% buy at least two defenders
constraint sum(p in Defenders)(bool2int(buy[p])) >= 2;

% buy at least three midfielders
constraint sum(p in Midfielders)(bool2int(buy[p])) >= 3;

% buy at least two strikers
constraint sum(p in Strikers)(bool2int(buy[p])) >= 2;

% buy at least eleven players in total
constraint sum(p in Players)(bool2int(buy[p])) >= 11;

% z: total price of the players bought
var 0..sum(price): z = sum(p in Players)(price[p] * bool2int(buy[p]));

% the purchases do not go over the chairman's limit
constraint z <= budget;

var int: objective = z;

solve maximize objective;

output ["{\"z\": ", showJSON(z), "}"];
