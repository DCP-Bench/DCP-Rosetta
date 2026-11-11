% diet: a MiniZinc model from DCP Rosetta.
%
% Given the prices and the nutritional requirements (at least) for each nutrition type, what is the
% optimal diet? The optimal diet is to minimize the cost of the products. Each food is bought in a whole
% number of units. The foods and their contents are:
%
%   Type of Food                   Calories  Chocolate (ounces)  Sugar (ounces)  Fat (ounces)
%   Chocolate Cake (1 slice)            400          3                   2             2
%   Chocolate ice cream (1 scoop)       200          2                   2             4
%   Cola (1 bottle)                     150          0                   4             1
%   Pineapple cheesecake (1 piece)      500          0                   4             5
%
% Save this file as model.mzn. Download `diet.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py diet.json
%   minizinc model.mzn diet_1.json

array[int] of int: price;                        % price[j]: the price of one unit of food j
array[int] of int: limits;                       % limits[k]: the minimum required of nutrition type k

set of int: Foods = index_set(price);            % the foods
set of int: Nutrients = index_set(limits);       % the nutrition types: calories, chocolate, sugar, fat

% content[j,k]: the amount of nutrition type k in one unit of food j
array[Foods, Nutrients] of int: content = [| 400, 3, 2, 2
                                           | 200, 2, 2, 4
                                           | 150, 0, 4, 1
                                           | 500, 0, 4, 5 |];

% buy[j]: the number of units of food j bought
array[Foods] of var int: buy;
var int: objective = sum(j in Foods)(price[j] * buy[j]);

% the units bought are not negative
constraint forall(j in Foods)(buy[j] >= 0);

% the diet provides at least the required amount of each nutrition type
constraint forall(k in Nutrients)(
    sum(j in Foods)(content[j, k] * buy[j]) >= limits[k]
);

solve minimize objective;
output ["{\"cost\": ", showJSON(objective), "}"];
