% revenue_maximization: a clingo model from DCP Rosetta.
%
% We have a set of flight legs (one-way non-stop flight) with a limited passenger capacity. According to market research, we defined a set of flight itineraries to sell as a package with a given price. For each package, we have an estimated demand. How many units of each package should we sell to maximize the revenue? We reserve the passenger seats according to the number of packages we want to sell.
%
% Save this file as model.lp. Download `revenue_maximization.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py revenue_maximization.json
%   python -m clingo model.lp revenue_maximization_1.lp

% Input: available_seats(J, S): the seats S available on flight leg J; demand(I, D): the estimated
% demand D for package I; revenue(I, R): the price R of one unit of package I; delta(I, J, K): the seats K that one unit of package I
% uses on flight leg J (indices are 0-based, as in the data).

% the units of each package sold are between 0 and its estimated demand
1 { packages_to_sell(I, V) : V = 0..D } 1 :- demand(I, D).

% the seats reserved on each flight leg do not exceed the seats available on it
:- available_seats(J, S), #sum { V*K,I : packages_to_sell(I, V), delta(I, J, K) } > S.

% the total revenue is the price of each unit times the units sold, summed over the packages
max_revenue(Z) :- Z = #sum { V*R,I : packages_to_sell(I, V), revenue(I, R) }.

% maximize the total revenue
#maximize { V*R,I : packages_to_sell(I, V), revenue(I, R) }.

#show packages_to_sell/2.
#show max_revenue/1.
