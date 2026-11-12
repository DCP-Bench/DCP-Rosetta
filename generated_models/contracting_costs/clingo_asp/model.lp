% contracting_costs: a clingo model from DCP Rosetta.
%
% A contractor planning the construction of a house found that he would have to pay: $1,100 to the paper hanger
% and the painter, $1,700 to the painter and plumber, $1,100 to the plumber and electrician, $3,300 to the
% electrician and carpenter, $5,300 to the carpenter and mason, and $3,200 to the mason and painter.
% What does each man charge for his services?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% pay(A,B,D): the contractor pays men A and B D dollars together
pay(paper_hanger,painter,1100).
pay(painter,plumber,1700).
pay(plumber,electrician,1100).
pay(electrician,carpenter,3300).
pay(carpenter,mason,5300).
pay(mason,painter,3200).

man(M) :- pay(M,_,_).
man(M) :- pay(_,M,_).

% each man charges a whole number of dollars, at most the largest payment of 5300
% dollars, and charges exactly one amount
1 { charge(M,V) : V = 0..5300 } 1 :- man(M).

% the two men of each pair are paid the given amount together: whatever the first
% charges, the second charges the rest of the payment
:- pay(A,B,D), charge(A,V), not charge(B,D-V).

% paper_hanger(V), painter(V), ...: the amount V that each man charges
paper_hanger(V) :- charge(paper_hanger,V).
painter(V) :- charge(painter,V).
plumber(V) :- charge(plumber,V).
electrician(V) :- charge(electrician,V).
carpenter(V) :- charge(carpenter,V).
mason(V) :- charge(mason,V).

#show paper_hanger/1.
#show painter/1.
#show plumber/1.
#show electrician/1.
#show carpenter/1.
#show mason/1.
