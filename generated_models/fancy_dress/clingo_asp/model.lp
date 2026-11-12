% fancy_dress: a clingo model from DCP Rosetta.
%
% Mr. Greenfan wants to give a dress party where the male guests must wear green dresses. The following rules are given: 1. If someone wears a green tie he has to wear a green shirt. 2. A guest who wears green socks or a green shirt must also wear a green tie or a green hat. 3. A guest wearing a green shirt or a green hat or who does not wear green socks must wear a green tie. 4. A guest who is not dressed according to rules 1-3 must pay a $11 entrance fee. Mr Greenguest wants to participate but owns only a green shirt (otherwise he would have to pay one for $9). He could buy a green tie for $10, a green hat (used) for $2 and green socks for $12. What is the cheapest solution for Mr Greenguest to participate?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% each item is worn (its atom is true) or not; the green shirt is owned, so wearing it costs nothing
{ tie; hat; shirt; socks; fee }.

% the cost of the items bought: a green tie $10, a green hat $2, green socks $12, the entrance fee $11
#minimize { 10,tie : tie; 2,hat : hat; 12,socks : socks; 11,fee : fee }.

% rule 1 is broken by a green tie without a green shirt
breaks1 :- tie, not shirt.

% rule 2 is broken by green socks or a green shirt without a green tie or a green hat
breaks2 :- socks, not tie, not hat.
breaks2 :- shirt, not tie, not hat.

% rule 3 is broken by a green shirt, a green hat, or no green socks, without a green tie
breaks3 :- shirt, not tie.
breaks3 :- hat, not tie.
breaks3 :- not socks, not tie.

% a guest who breaks any of rules 1-3 must pay the entrance fee
:- breaks1, not fee.
:- breaks2, not fee.
:- breaks3, not fee.

% the outputs: each item as true (worn or paid) or false
t(true) :- tie.
t(false) :- not tie.
h(true) :- hat.
h(false) :- not hat.
r(true) :- shirt.
r(false) :- not shirt.
s(true) :- socks.
s(false) :- not socks.
n(true) :- fee.
n(false) :- not fee.

#show t/1.
#show h/1.
#show r/1.
#show s/1.
#show n/1.
