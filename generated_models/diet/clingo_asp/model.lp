% diet: a clingo model from DCP Rosetta.
%
% Given the prices and the minimum nutritional requirements for each nutrition type, find the optimal diet:
% the choice of whole numbers of units of the foods that meets every requirement at the lowest total cost.
% The foods, with their contents per unit in calories, chocolate (ounces), sugar (ounces) and fat (ounces),
% are: chocolate cake (1 slice) 400, 3, 2, 2; chocolate ice cream (1 scoop) 200, 2, 2, 4; cola (1 bottle)
% 150, 0, 4, 1; pineapple cheesecake (1 piece) 500, 0, 4, 5.
%
% Save this file as model.lp. Download `diet.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py diet.json
%   python -m clingo model.lp diet_1.lp

% Input: n(N): the number N of foods, numbered 0..N-1; price(F, P): the price P of one unit of food F;
% limits(L, R): the least amount R required of nutrient L (0 calories, 1 chocolate, 2 sugar, 3 fat).

food(0..N-1) :- n(N).

% content(F, L, Q): one unit of food F holds Q of nutrient L, as in the table of the problem
content(0,0,400). content(0,1,3). content(0,2,2). content(0,3,2).
content(1,0,200). content(1,1,2). content(1,2,2). content(1,3,4).
content(2,0,150). content(2,1,0). content(2,2,4). content(2,3,1).
content(3,0,500). content(3,1,0). content(3,2,4). content(3,3,5).

% reach(F, L, U): the least number of units of food F that alone reach the requirement of nutrient L
reach(F,L,(R+Q-1)/Q) :- food(F), content(F,L,Q), Q > 0, limits(L,R).

% K: the largest of these over all foods and nutrients
largest_reach(K) :- K = #max { C,F,L : reach(F,L,C) }.

% the number of units of a food is at most K+1: with more than K+1 units, removing one unit leaves at
% least K units, which alone reach the requirement of every nutrient the food holds, and the cost does not rise
amount(0..K+1) :- largest_reach(K).

% the number of units of each food is exactly one amount
1 { units(F,V) : amount(V) } 1 :- food(F).

% every nutrient reaches its minimum amount
:- limits(L,R), #sum { Q*V,F : units(F,V), content(F,L,Q) } < R.

% cost(S): the total price S of the diet
cost(S) :- S = #sum { P*V,F : units(F,V), price(F,P) }.

#minimize { P*V,F : units(F,V), price(F,P) }.

#show cost/1.
