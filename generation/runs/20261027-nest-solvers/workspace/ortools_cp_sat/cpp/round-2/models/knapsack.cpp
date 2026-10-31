#include <cstdint>
#include <fstream>
#include <iostream>
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
  const auto weights = instance.at("weights").get<std::vector<int64_t>>();
  const auto values = instance.at("values").get<std::vector<int64_t>>();
  const int64_t capacity = instance.at("capacity").get<int64_t>();
  const int n = static_cast<int>(weights.size());

  CpModelBuilder model;
  std::vector<BoolVar> take;
  LinearExpr weight;
  LinearExpr value;
  for (int i = 0; i < n; ++i) {
    take.push_back(model.NewBoolVar());
    weight += weights[i] * take[i];
    value += values[i] * take[i];
  }
  model.AddLessOrEqual(weight, capacity);
  model.Maximize(value);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cerr << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  std::cout << "{\"take\": [";
  for (int i = 0; i < n; ++i) {
    std::cout << (i ? ", " : "") << SolutionBooleanValue(response, take[i]);
  }
  std::cout << "]}\n";
  return 0;
}
