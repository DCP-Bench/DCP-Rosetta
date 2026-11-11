% curious_set_of_integers: a MiniZinc model from DCP Rosetta.
%
% The integers 1, 3, 8 and 120 form a set with a remarkable property: the product of any two integers is
% one less than a perfect square. Find a fifth number (larger than or equal to 0) that can be added to the
% set without destroying this property.
%
% Save this file as model.mzn. Download `curious_set_of_integers.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py curious_set_of_integers.json
%   minizinc model.mzn curious_set_of_integers_1.json

int: max_val;                                    % the largest value the fifth number may take

set of int: Known = {1, 3, 8, 120};              % the four members of the set
int: max_product = max(Known) * max_val + 1;     % the largest product plus one that can occur
int: max_root = ceil(sqrt(int2float(max_product)));  % the largest square root that can occur

var 0..max_val: extra;                           % the fifth number

% the fifth number is not already a member of the set
constraint forall(k in Known)(extra != k);

% the product of the fifth number and each member is one less than a perfect square
constraint forall(k in Known)(
    exists(r in 0..max_root)(r * r = extra * k + 1)
);

solve satisfy;
output ["{\"number\": ", showJSON(extra), "}"];
