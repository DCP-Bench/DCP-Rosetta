% session3_exodus: a MiniZinc model from DCP Rosetta.
%
% In preparation for Passover, five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) have been
% chosen to present different parts of the story of the Exodus from Egypt (burning bush, captivity, Moses's
% youth, Passover, or the Ten Commandments). Each child is a different age (three, five, seven, eight, or ten),
% and the family of each child has recently made its own exodus to America from a different country (Ethiopia,
% Kazakhstan, Lithuania, Morocco, or Yemen). Find the age of each child, his or her family's country of origin,
% and the part of the Exodus story each related, from these clues:
% 1. Debby's family is from Lithuania.
% 2. The child who told the story of the Passover is two years older than Bernice.
% 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
% 4. The child from the Moroccan family is three years older than Ted.
% 5. Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: n = 5;                                  % five children, five ages, five countries and five stories

% Each category is a list of five values 1..5, one per slot of that category; equal values in two
% categories name the same child. ages[k]: the child of age age_years[k]; children[c]: the child
% number of the c-th child in the order Bernice, Carl, Debby, Sammy, Ted; countries[c] and stories[c]
% are read the same way, in the orders Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen and burning
% bush, captivity, Moses's youth, Passover, Ten Commandments.
array[1..n] of var 1..n: ages;
array[1..n] of var 1..n: children;
array[1..n] of var 1..n: countries;
array[1..n] of var 1..n: stories;

array[1..n] of int: age_years = [3, 5, 7, 8, 10];   % the possible ages, in the slot order of ages

% names for the slots used in the clues
var 1..n: bernice = children[1];
var 1..n: debby = children[3];
var 1..n: sammy = children[4];
var 1..n: ted = children[5];
var 1..n: ethiopia = countries[1];
var 1..n: lithuania = countries[3];
var 1..n: morocco = countries[4];
var 1..n: yemen = countries[5];
var 1..n: moses_youth = stories[3];
var 1..n: passover = stories[4];

% each age, child, country and story is used by exactly one child
constraint all_different(ages);
constraint all_different(children);
constraint all_different(countries);
constraint all_different(stories);

% 1. Debby's family is from Lithuania
constraint debby = lithuania;

% 2. the child who told the story of the Passover is two years older than Bernice
constraint forall(i, j in 1..n)
    (ages[i] = passover /\ ages[j] = bernice -> age_years[i] = age_years[j] + 2);

% 3. the child whose family is from Yemen is younger than the child from the Ethiopian family
constraint forall(i, j in 1..n)
    (ages[i] = yemen /\ ages[j] = ethiopia -> age_years[i] < age_years[j]);

% 4. the child from the Moroccan family is three years older than Ted
constraint forall(i, j in 1..n)
    (ages[i] = morocco /\ ages[j] = ted -> age_years[i] = age_years[j] + 3);

% 5. Sammy is three years older than the child who told the story of Moses's youth
constraint forall(i, j in 1..n)
    (ages[i] = sammy /\ ages[j] = moses_youth -> age_years[i] = age_years[j] + 3);

solve satisfy;
output ["{\"ages\": ", showJSON(ages), ", \"children\": ", showJSON(children),
        ", \"countries\": ", showJSON(countries), ", \"stories\": ", showJSON(stories), "}"];
