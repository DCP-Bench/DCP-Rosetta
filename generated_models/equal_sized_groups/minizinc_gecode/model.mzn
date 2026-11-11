% equal_sized_groups: a MiniZinc model from DCP Rosetta.
%
% A sorted list of N elements is to be divided into K groups by choosing K-1 break points between
% them. Elements with the same value must be in the same group, and each group holds at least one
% element. Find K groups as close in size to round(N/K) as possible: the total error, the sum over
% the groups of the difference between the group size and round(N/K), is to be minimized. A break
% point is the number of elements before it.
%
% Save this file as model.mzn. Download `equal_sized_groups.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py equal_sized_groups.json
%   minizinc model.mzn equal_sized_groups_1.json

int: k;                                       % the number of groups
array[int] of int: a;                         % the sorted values, a[i] for element i
int: n = length(a);                           % the number of elements

set of int: Groups = 1..k;                    % the groups, numbered from 1
% round(n / k), with an exact half rounded to the even integer as Python's round() does
int: quotient = n div k;
int: twice_remainder = 2 * (n mod k);
int: ideal_size =
    if twice_remainder < k then quotient
    elseif twice_remainder > k then quotient + 1
    elseif quotient mod 2 = 0 then quotient
    else quotient + 1 endif;

% bound[g]: the number of elements before group g + 1 (bound[0] = 0, bound[k] = n)
array[0..k] of var 0..n: bound;
% x[p]: the break point between group p and group p + 1
array[1..k - 1] of var 1..n - 1: x;

% a break point after element j is allowed only where the value changes
set of int: CutPoints = {j | j in 1..n - 1 where a[j] != a[j + 1]};

% the groups start at zero and end with the last element
constraint bound[0] = 0;
constraint bound[k] = n;
% the break points are the bounds between the groups
constraint forall(p in 1..k - 1) (x[p] = bound[p]);
% elements with the same value stay in the same group
constraint forall(p in 1..k - 1) (x[p] in CutPoints);
% each group holds at least one element
constraint forall(g in Groups) (bound[g] > bound[g - 1]);

% the total error is the sum of the differences from the ideal group size
var int: objective = sum(g in Groups)(abs(bound[g] - bound[g - 1] - ideal_size));

solve minimize objective;
output ["{\"x\": ", showJSON([x[p] | p in 1..k - 1]), "}"];
