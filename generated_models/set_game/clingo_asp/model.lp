% set_game: a clingo model from DCP Rosetta.
%
% Set (stylized as SET or SET!) is a real-time card game designed by Marsha Falco in 1974 and published by Set Enterprises in 1991. The deck consists of 81 unique cards that vary in four features across three possibilities for each kind of feature: number of shapes (one, two, or three), shape (diamond, squiggle, oval), shading (solid, striped, or open), and color (red, green, or purple). Each possible combination of features (e.g. a card with three striped green diamonds) appears as a card precisely once in the deck.
%
% In the game, certain combinations of three cards are said to make up a "set". For each one of the four categories of features (color, number, shape, and shading), the three cards must display that feature as either a) all the same, or b) all different. Put another way: For each feature the three cards must avoid having two cards showing one version of the feature and the remaining card showing a different version.
%
% Given a list of cards, each written as [number, shading, color, shape], find three different cards that form a set.
%
% Save this file as model.lp. Download `set_game.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py set_game.json
%   python -m clingo model.lp set_game_1.lp
%
% Input: cards_data(I, F, V) holds the value V (1 to 3) of feature F of card I, where F is 0 for number,
% 1 for shading, 2 for color and 3 for shape (indices are 0-based, as in the data).

card(I) :- cards_data(I, _, _).

% the three winning cards take the slots 0, 1 and 2, one card for each slot
slot(0..2).
1 { winning_cards(K, I) : card(I) } 1 :- slot(K).

% each card is in at most one slot, so the three cards are different
:- card(I), #count { K : winning_cards(K, I) } > 1.

% the value of each feature on each of the three winning cards
value_on_slot(K, F, V) :- winning_cards(K, I), cards_data(I, F, V).

% for each feature, the three cards are all the same or all different: two cards with one value
% and the third card with another value is not allowed
:- value_on_slot(K1, F, V), value_on_slot(K2, F, V), value_on_slot(K3, F, W),
   K1 < K2, K3 != K1, K3 != K2, V != W.

#show winning_cards/2.
