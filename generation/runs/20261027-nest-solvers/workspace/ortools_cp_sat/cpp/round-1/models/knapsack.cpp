// 0/1 knapsack: maximise total value within the capacity.
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

  CpModelBuilder model;
  std::vector<BoolVar> take;
  LinearExpr weight_total;
  LinearExpr value_total;
  for (size_t i = 0; i < weights.size(); ++i) {
    take.push_back(model.NewBoolVar());
    weight_total += weights[i] * take.back();
    value_total += values[i] * take.back();
  }
  model.AddLessOrEqual(weight_total, capacity);
  model.Maximize(value_total);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  nlohmann::json out;
  out["take"] = nlohmann::json::array();
  for (const BoolVar& t : take) out["take"].push_back(SolutionBooleanValue(response, t) ? 1 : 0);
  std::cout << out.dump() << "\n";
  return 0;
}
