% session5_grocery: a clingo model from DCP Rosetta.
%
% A kid goes into a grocery store and buys a number of items. The cashier charges a total price, the kid pays and is about to leave when the cashier calls the kid back, and says "Hold on, I multiplied the items instead of adding them; I'll try again; Hah, with adding them the price still comes to the same total price". What were the prices of the items?
%
% Each price is a positive whole number of cents, and total_price is given in cents. Both the sum and the product of the prices in dollars equal the total price in dollars.
%
% Save this file as model.lp. Download `session5_grocery.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session5_grocery.json
%   python -m clingo model.lp session5_grocery_1.lp
%
% Input: num_items(K) holds the number K of items; total_price(T) holds the total price T in cents
% (indices are 0-based, as in the data).

item(0..K-1) :- num_items(K).

% each price is a positive whole number of cents, at most the total since the prices add up to it
value(1..T) :- total_price(T).

% each item has exactly one price
1 { prices(I, V) : value(V) } 1 :- item(I).

% the prices in cents add up to the total price in cents, so that the sum in dollars equals the total in dollars
:- total_price(T), #sum { V, I : prices(I, V) } != T.

% the product of the prices in dollars equals the total price in dollars, so the product of the prices in
% cents is the total price times 100 for each item after the first (each price in dollars is its cents / 100)
target(T * 100 ** (K - 1)) :- num_items(K), total_price(T).

% running product of the first prices in cents; the product of some of the prices divides the product of all
% of them, so a running product that does not divide the target is dropped
running(0, V) :- prices(0, V), target(P), P \ V == 0.
running(I, X) :- item(I), I > 0, running(I - 1, Y), prices(I, V), target(P), X = Y * V, P \ X == 0.

% the product of all the prices is the target
final(X) :- num_items(K), running(K - 1, X).
:- target(P), not final(P).

#show prices/2.
