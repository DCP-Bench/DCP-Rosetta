% birthday_coins: a MiniZinc model from DCP Rosetta.
%
% Tommy was given 15 coins for his birthday. Each coin is a half-crown, a shilling or a sixpence, but he
% was not necessarily given coins of all three kinds. When he added it up, he found that he had
% 1 pound 5 shillings and 6 pence. How many half-crowns could he have been given?
%
% A pound is 20 shillings and a shilling is 12 pence, so a pound is 240 pence. A half-crown is
% 2 shillings and sixpence, which is 30 pence; a shilling is 12 pence; a sixpence is 6 pence.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

int: num_coins = 15;                          % the number of coins given
int: total_pence = 240 + 5 * 12 + 6;          % 1 pound 5 shillings and 6 pence, in pence

int: half_crown_pence = 30;
int: shilling_pence = 12;
int: sixpence_pence = 6;

var 0..num_coins: half_crowns;                % the number of half-crowns given
var 0..num_coins: shillings;                  % the number of shillings given
var 0..num_coins: sixpences;                  % the number of sixpences given

% the coins are fifteen in all
constraint half_crowns + shillings + sixpences = num_coins;

% the coins add up to 1 pound 5 shillings and 6 pence
constraint half_crown_pence * half_crowns + shilling_pence * shillings + sixpence_pence * sixpences = total_pence;

solve satisfy;
output ["{\"half_crowns\": ", showJSON(half_crowns), "}"];
