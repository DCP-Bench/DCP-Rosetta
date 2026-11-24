% set_game: a MiniZinc model from DCP Rosetta.
%
% Set is a card game. The deck has 81 unique cards that vary in four features (number, shading, color and
% shape), each feature with three possible values, and each combination of features appears once. Three cards
% form a set when, for each of the four features, the three cards show that feature either all the same or all
% different. Given a list of cards, each written as [number, shading, color, shape], find three different cards
% that form a set.
%
% Save this file as model.mzn. Download `set_game.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py set_game.json
%   minizinc model.mzn set_game_1.json

include "globals.mzn";

array[int, int] of int: cards_data;             % cards_data[c, f]: value of feature f of card c (f = 1..4)
int: n_cards = card(index_set_1of2(cards_data));  % the number of cards on the table

% winning_cards[k]: the position of the k-th chosen card, counted from 0 (card c is row c + 1 of cards_data)
array[1..3] of var 0..n_cards - 1: winning_cards;

% the three chosen cards are different cards
constraint all_different(winning_cards);

% for each of the four features, the three chosen cards all show the same value or all different values
constraint forall(f in 1..4)(
    let { var int: a = cards_data[winning_cards[1] + 1, f];
          var int: b = cards_data[winning_cards[2] + 1, f];
          var int: c = cards_data[winning_cards[3] + 1, f] }
    in (a = b /\ b = c) \/ all_different([a, b, c])
);

solve satisfy;
output ["{\"winning_cards\": ", showJSON(winning_cards), "}"];
