% session3_people_in_a_room: a MiniZinc model from DCP Rosetta.
%
% There are 13 people, 4 of them male. They randomly enter a room one at a time. Find a way that the males
% and females enter so that the ratio of females to males in the room at any one time is no greater than 7/3.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

int: total_people = 13;                          % the number of people
int: num_males = 4;                              % the number of male people
int: num_females = total_people - num_males;     % the number of female people

set of int: Arrivals = 1..total_people;          % the positions in the order of entry

% sequence[k]: the k-th person to enter is female (false: male)
array[Arrivals] of var bool: sequence;

% the people entering the room are the 13 people: 4 male and the rest female
constraint sum(k in Arrivals)(bool2int(sequence[k])) = num_females;

% at any one time the ratio of females to males in the room is no greater than 7/3, written
% without division as 3 females <= 7 males, for every prefix of the entry order
constraint forall(k in Arrivals)(
    let { var int: females = sum(j in 1..k)(bool2int(sequence[j])),
          var int: males = k - females }
    in 3 * females <= 7 * males
);

solve satisfy;
output ["{\"sequence\": ", showJSON(sequence), "}"];
