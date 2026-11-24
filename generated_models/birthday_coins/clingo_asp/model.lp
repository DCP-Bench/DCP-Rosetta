% birthday_coins: a clingo model from DCP Rosetta.
%
% Tommy was given 15 coins for his birthday. Each coin is a half-crown, a shilling or a sixpence, but he was not necessarily given coins of all three kinds. When he added it up, he found that he had £1 5s 6d (one pound 5 shillings and 6 pence). How many half-crowns could he have been given? A pound is 20 shillings and a shilling is 12 pence, so a pound is 240 pence. A half-crown is 2 shillings and sixpence, so it is 30 pence. A shilling is 12 pence and a sixpence is 6 pence.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the number of half-crowns, shillings and sixpences Tommy was given, each from 0 to 15
1 { half_crowns(H) : H = 0..15 } 1.
1 { shillings(S) : S = 0..15 } 1.
1 { sixpences(P) : P = 0..15 } 1.

% the coins are 15 in total
:- half_crowns(H), shillings(S), sixpences(P), H + S + P != 15.

% the coins add up to £1 5s 6d, which is 306 pence
:- half_crowns(H), shillings(S), sixpences(P), 30 * H + 12 * S + 6 * P != 306.

#show half_crowns/1.
