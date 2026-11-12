% capital_budget: a clingo model from DCP Rosetta.
%
% A company is considering a number of investments. Each investment will yield a net present value (NPV).
% Each investment requires a certain cash outflow at the present time. There is a total budget available for
% investment. How to maximize the NPV obtained from the investments?
%
% Save this file as model.lp. Download `capital_budget.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py capital_budget.json
%   python -m clingo model.lp capital_budget_1.lp

% Input: budget(B) holds the total budget B; cash_flow(I, C) says that investment I needs the cash outflow C
% now; npv(I, V) says that investment I yields the net present value V (indices are 0-based, as in the data).

investment(I) :- npv(I, _).

% each investment is either chosen or not
{ chosen(I) } :- investment(I).

% the cash outflows of the chosen investments do not exceed the budget
:- budget(B), #sum { C, I : chosen(I), cash_flow(I, C) } > B.

% z: the total NPV of the chosen investments, which is as large as possible
z(Z) :- Z = #sum { V, I : chosen(I), npv(I, V) }.
#maximize { Z : z(Z) }.

% x(I, true) if investment I is chosen, x(I, false) otherwise
x(I, true) :- chosen(I).
x(I, false) :- investment(I), not chosen(I).

#show x/2.
#show z/1.
