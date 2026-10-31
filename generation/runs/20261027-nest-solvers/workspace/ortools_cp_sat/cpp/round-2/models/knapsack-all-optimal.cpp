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

struct Knapsack {
  std::vector<int64_t> weights;
  std::vector<int64_t> values;
  int64_t capacity;
};

// Adds the take variables, the capacity constraint and returns the value expression.
LinearExpr BuildKnapsack(CpModelBuilder& model, const Knapsack& k,
                         std::vector<BoolVar>& take) {
  const int n = static_cast<int>(k.weights.size());
  LinearExpr weight;
  LinearExpr value;
  for (int i = 0; i < n; ++i) {
    take.push_back(model.NewBoolVar());
    weight += k.weights[i] * take[i];
    value += k.values[i] * take[i];
  }
  model.AddLessOrEqual(weight, k.capacity);
  return value;
}

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: " << argv[0] << " INSTANCE.json\n";
    return 2;
  }
  std::ifstream in(argv[1]);
  const nlohmann::json instance = nlohmann::json::parse(in);
  const Knapsack k{instance.at("weights").get<std::vector<int64_t>>(),
                   instance.at("values").get<std::vector<int64_t>>(),
                   instance.at("capacity").get<int64_t>()};
  const int n = static_cast<int>(k.weights.size());

  // Pass 1: the optimum z*.
  int64_t best = 0;
  {
    CpModelBuilder model;
    std::vector<BoolVar> take;
    const LinearExpr value = BuildKnapsack(model, k, take);
    model.Maximize(value);
    const CpSolverResponse response = Solve(model.Build());
    if (response.status() != CpSolverStatus::OPTIMAL) {
      std::cerr << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
      return 1;
    }
    best = SolutionIntegerValue(response, value);
  }

  // Pass 2: a fresh model with the value fixed to z* and no objective, enumerated.
  CpModelBuilder model;
  std::vector<BoolVar> take;
  const LinearExpr value = BuildKnapsack(model, k, take);
  model.AddEquality(value, best);

  Model enumerator;
  enumerator.Add(NewFeasibleSolutionObserver([&](const CpSolverResponse& r) {
    std::cout << "{\"take\": [";
    for (int i = 0; i < n; ++i) {
      std::cout << (i ? ", " : "") << SolutionBooleanValue(r, take[i]);
    }
    std::cout << "]}\n";
  }));
  SatParameters parameters;
  parameters.set_enumerate_all_solutions(true);
  parameters.set_num_workers(1);
  enumerator.Add(NewSatParameters(parameters));

  const CpSolverResponse response = SolveCpModel(model.Build(), &enumerator);
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cerr << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  return 0;
}
