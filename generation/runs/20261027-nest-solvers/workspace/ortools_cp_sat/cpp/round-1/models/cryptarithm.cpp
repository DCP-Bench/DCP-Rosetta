// Addition cryptarithm: assign distinct digits to letters so that the addends sum to the sum.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: " << argv[0] << " INSTANCE.json\n";
    return 2;
  }
  std::ifstream in(argv[1]);
  const nlohmann::json instance = nlohmann::json::parse(in);
  const std::vector<std::string> addends =
      instance.at("addends").get<std::vector<std::string>>();
  const std::string sum = instance.at("sum").get<std::string>();

  std::set<char> letters;
  for (const std::string& word : addends) letters.insert(word.begin(), word.end());
  letters.insert(sum.begin(), sum.end());

  CpModelBuilder model;
  std::map<char, IntVar> digit;
  std::vector<LinearExpr> all_digits;
  for (char letter : letters) {
    digit.emplace(letter, model.NewIntVar(Domain(0, 9)));
    all_digits.push_back(digit.at(letter));
  }
  model.AddAllDifferent(all_digits);

  // No multi-letter word may start with 0.
  auto forbid_leading_zero = [&](const std::string& word) {
    if (word.size() > 1) model.AddNotEqual(digit.at(word[0]), 0);
  };
  for (const std::string& word : addends) forbid_leading_zero(word);
  forbid_leading_zero(sum);

  // sum(addend values) - value(sum) == 0, where a word's value is the sum of digit * 10^place.
  LinearExpr balance;
  auto add_word = [&](const std::string& word, int64_t sign) {
    int64_t place = 1;
    for (auto it = word.rbegin(); it != word.rend(); ++it) {
      balance += (sign * place) * digit.at(*it);
      place *= 10;
    }
  };
  for (const std::string& word : addends) add_word(word, 1);
  add_word(sum, -1);
  model.AddEquality(balance, 0);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() == CpSolverStatus::INFEASIBLE) {
    std::cout << "{\"status\": \"unsatisfiable\"}\n";
    return 0;
  }
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  nlohmann::json out;
  for (const auto& [letter, var] : digit) {
    out["digits"][std::string(1, letter)] = SolutionIntegerValue(response, var);
  }
  std::cout << out.dump() << "\n";
  return 0;
}
