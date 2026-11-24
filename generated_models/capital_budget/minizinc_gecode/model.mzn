% capital_budget: a MiniZinc model from DCP Rosetta.
%
% A company is considering a number of investments. Each investment will yield a net present value (NPV).
% Each investment requires a certain cash outflow at the present time. There is a total budget available
% for investment. How to maximize the NPV obtained from the investments?
%
% Save this file as model.mzn. Download `capital_budget.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py capital_budget.json
%   minizinc model.mzn capital_budget_1.json

int: budget;                                 % the total cash available for investment
array[int] of int: cash_flow;                % cash_flow[i]: the cash outflow of investment i at the present time
array[int] of int: npv;                      % npv[i]: the net present value of investment i

set of int: Investments = index_set(cash_flow);

% x[i]: investment i is chosen
array[Investments] of var bool: x;

% z: the total net present value of the chosen investments
var int: z = sum(i in Investments)(npv[i] * bool2int(x[i]));
var int: objective = z;

% the cash outflows of the chosen investments do not exceed the budget
constraint sum(i in Investments)(cash_flow[i] * bool2int(x[i])) <= budget;

solve maximize objective;

output ["{\"x\": ", showJSON(x), ", \"z\": ", showJSON(z), "}"];
