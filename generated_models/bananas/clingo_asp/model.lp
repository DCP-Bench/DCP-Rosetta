% bananas: a clingo model from DCP Rosetta.
%
% Five bananas cost three dollars, seven oranges cost five dollars, nine mangoes cost seven dollars, and three apples cost nine dollars. I need to purchase 100 fruits in 100 dollars. Please keep in mind that all types of fruits need to be purchased, but I do not like banana and apple, so the number of bananas and apples together should be as small as possible.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% each type of fruit is bought in a number of at least one and at most 100
1 { bananas(N) : N = 1..100 } 1.
1 { oranges(N) : N = 1..100 } 1.
1 { mangoes(N) : N = 1..100 } 1.
1 { apples(N) : N = 1..100 } 1.

% the total number of fruits bought is 100
:- #sum { N,bananas : bananas(N); N,oranges : oranges(N); N,mangoes : mangoes(N); N,apples : apples(N) } != 100.

% the total cost is 100 dollars; the prices are scaled by 315 so that they are whole numbers
% (a banana costs 3/5 of a dollar, an orange 5/7, a mango 7/9 and an apple 3 dollars)
:- #sum { 189*N,bananas : bananas(N); 225*N,oranges : oranges(N); 245*N,mangoes : mangoes(N); 945*N,apples : apples(N) } != 31500.

% the number of bananas and apples together is as small as possible
#minimize { N,bananas : bananas(N); N,apples : apples(N) }.

#show bananas/1.
#show oranges/1.
#show mangoes/1.
#show apples/1.
