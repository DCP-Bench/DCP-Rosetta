% fancy_dress: a MiniZinc model from DCP Rosetta.
%
% Mr. Greenfan wants to give a dress party where the male guests must wear green dresses. The
% following rules are given:
% 1. If someone wears a green tie he has to wear a green shirt.
% 2. A guest who wears green socks or a green shirt must also wear a green tie or a green hat.
% 3. A guest wearing a green shirt or a green hat or who does not wear green socks must wear a
%    green tie.
% 4. A guest who is not dressed according to rules 1-3 must pay a $11 entrance fee.
% Mr Greenguest wants to participate but owns only a green shirt (otherwise he would have to pay
% one for $9). He could buy a green tie for $10, a green hat (used) for $2 and green socks for $12.
% What is the cheapest solution for Mr Greenguest to participate?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

var bool: t;                                  % t: he wears a green tie (bought for $10)
var bool: h;                                  % h: he wears a green hat (bought for $2)
var bool: r;                                  % r: he wears the green shirt he owns (costs nothing)
var bool: s;                                  % s: he wears green socks (bought for $12)
var bool: n;                                  % n: he pays the $11 entrance fee

% rule 1, unless he pays the entrance fee: a green tie needs a green shirt
constraint (t -> r) \/ n;
% rule 2, unless he pays the entrance fee: green socks or a green shirt need a green tie or hat
constraint ((s \/ r) -> (t \/ h)) \/ n;
% rule 3, unless he pays the entrance fee: a green shirt, a green hat or no green socks need a tie
constraint (r \/ h \/ not s) -> (t \/ n);

% the total cost of the tie, hat, socks and entrance fee (the shirt is already owned)
var int: objective = 10 * bool2int(t) + 2 * bool2int(h) + 12 * bool2int(s) + 11 * bool2int(n);

solve minimize objective;
output ["{\"t\": ", showJSON(t), ", \"h\": ", showJSON(h), ", \"r\": ", showJSON(r),
        ", \"s\": ", showJSON(s), ", \"n\": ", showJSON(n), "}"];
