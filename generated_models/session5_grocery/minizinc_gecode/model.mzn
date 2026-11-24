% session5_grocery: a MiniZinc model from DCP Rosetta.
%
% A kid goes into a grocery store and buys a number of items. The cashier charges a total price, the kid pays
% and is about to leave when the cashier calls the kid back and says "Hold on, I multiplied the items instead
% of adding them; I'll try again; Hah, with adding them the price still comes to the same total price". What
% were the prices of the items?
%
% Each price is a positive whole number of cents, and total_price is given in cents. Both the sum and the
% product of the prices in dollars equal the total price in dollars.
%
% Save this file as model.mzn. Download `session5_grocery.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session5_grocery.json
%   minizinc model.mzn session5_grocery_1.json

int: total_price;                               % the total price, in cents
int: num_items;                                 % the number of items bought
int: cents_per_dollar = 100;                    % cents in one dollar

set of int: Items = 1..num_items;               % one index per item

% prices[i]: the price of item i, in cents
array[Items] of var 1..total_price: prices;

% the sum of the prices in dollars equals the total price in dollars
constraint sum(i in Items)(prices[i]) = total_price;

% the product of the prices in dollars equals the total price in dollars: prod(prices[i] / 100) =
% total_price / 100, which multiplied by 100^num_items is prod(prices[i]) = total_price * 100^(num_items - 1)
constraint product(i in Items)(prices[i]) = total_price * pow(cents_per_dollar, num_items - 1);

solve satisfy;
output ["{\"prices\": ", showJSON(prices), "}"];
