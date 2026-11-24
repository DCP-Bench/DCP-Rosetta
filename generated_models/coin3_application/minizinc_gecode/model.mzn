% coin3_application: a MiniZinc model from DCP Rosetta.
%
% Find the minimum number of coins that allows one to pay exactly any amount smaller than a given
% maximum amount using a given set of denominations.
%
% Save this file as model.mzn. Download `coin3_application.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py coin3_application.json
%   minizinc model.mzn coin3_application_1.json

array[int] of int: denominations;               % denominations[i]: value of the coins of type i
int: max_amount_to_pay;                         % every amount smaller than this must be payable

set of int: Types = index_set(denominations);   % one index per coin type
int: n = card(Types);
set of int: Amounts = 0..max_amount_to_pay - 1; % amounts 0 to max_amount_to_pay - 1
int: never = max_amount_to_pay;                 % "no number of coins pays this amount"

% x[j]: number of coins of type j used (at most max_amount_to_pay - 1: no amount needs more coins of one type, implied bound)
array[Types] of var 0..max_amount_to_pay - 1: x;

% can[j, v]: amount v can be paid with the coins of types 1 to j
array[0..n, Amounts] of var bool: can;
% needed[j, v]: fewest coins of type j which, with the coins of types before j, pay amount v
array[Types, Amounts] of var 0..never: needed;

% with no coin types only amount 0 can be paid
constraint forall(v in Amounts)(can[0, v] <-> v = 0);

% amount v is paid with no coin of type j if the types before j pay it, otherwise with one more
% coin of type j than the amount v - denominations[j] needs
constraint forall(j in Types, v in Amounts)(
    needed[j, v] = if can[j - 1, v] then 0
                   elseif v >= denominations[j] then min(needed[j, v - denominations[j]] + 1, never)
                   else never endif);

% amount v can be paid with the coins of types 1 to j when enough coins of type j are used
constraint forall(j in Types, v in Amounts)(can[j, v] <-> needed[j, v] <= x[j]);

% every amount smaller than the maximum is paid exactly with the coins used
constraint forall(a in 1..max_amount_to_pay - 1)(can[n, a]);

var int: objective = sum(j in Types)(x[j]);

solve minimize objective;

output ["{\"x\": ", showJSON(x), "}"];
