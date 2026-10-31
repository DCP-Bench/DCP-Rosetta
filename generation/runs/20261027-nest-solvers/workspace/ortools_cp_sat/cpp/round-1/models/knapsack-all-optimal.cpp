// 0/1 knapsack: print every optimal selection, one JSON object per line.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>

#include <nlohmann/json.hpp>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"
#include "ortools/sat/model.h"
#include "ortools/sat/sat_parameters.pb.h"

using namespace operations_research;
using namespace operations_research::sat;

namespace {

// Adds the item flags and the capacity constraint. Fills in the flags and the value expression.
void BuildKnapsack(CpModelBuilder& model, const std::vector<int64_t>& weights,
                   const std::vector<int64_t>& values, int64_t capacity,
                   std::vector<BoolVar>& take, LinearExpr& value_total) {
  LinearExpr weight_total;
  for (size_t i = 0; i < weights.size(); ++i) {
    take.push_back(model.NewBoolVar());
    weight_total += weights[i] * take.back();
    value_total += values[i] * take.back();
  }
  model.AddLessOrEqual(weight_total, capacity);
}

}  // namespace

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

  // Phase 1: the optimum.
  CpModelBuilder first;
  std::vector<BoolVar> take_first;
  LinearExpr value_first;
  BuildKnapsack(first, weights, values, capacity, take_first, value_first);
  first.Maximize(value_first);
  const CpSolverResponse best = Solve(first.Build());
  if (best.status() != CpSolverStatus::OPTIMAL) {
    std::cout << "Status: " << CpSolverStatus_Name(best.status()) << "\n";
    return 1;
  }
  const int64_t optimum = static_cast<int64_t>(best.objective_value());

  // Phase 2: a fresh model with the value fixed to the optimum and no objective.
  CpModelBuilder second;
  std::vector<BoolVar> take;
  LinearExpr value_total;
  BuildKnapsack(second, weights, values, capacity, take, value_total);
  second.AddEquality(value_total, optimum);

  Model enumerator;
  enumerator.Add(NewFeasibleSolutionObserver([&](const CpSolverResponse& r) {
    nlohmann::json out;
    out["take"] = nlohmann::json::array();
    for (const BoolVar& t : take) out["take"].push_back(SolutionBooleanValue(r, t) ? 1 : 0);
    std::cout << out.dump() << "\n";
  }));
  SatParameters parameters;
  parameters.set_enumerate_all_solutions(true);
  parameters.set_num_workers(1);
  enumerator.Add(NewSatParameters(parameters));
  const CpSolverResponse response = SolveCpModel(second.Build(), &enumerator);
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  return 0;
}
