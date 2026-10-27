#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <utility>
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
  // jobs[j][k] = (machine, duration) of task k of job j.
  const auto jobs =
      instance.at("jobs").get<std::vector<std::vector<std::pair<int, int64_t>>>>();

  int64_t horizon = 0;
  int n_machines = 0;
  for (const auto& job : jobs) {
    for (const auto& [machine, duration] : job) {
      horizon += duration;
      n_machines = std::max(n_machines, machine + 1);
    }
  }

  CpModelBuilder model;
  std::vector<std::vector<IntVar>> start(jobs.size());
  std::vector<std::vector<IntervalVar>> on_machine(n_machines);
  const IntVar makespan = model.NewIntVar(Domain(0, horizon));

  for (size_t j = 0; j < jobs.size(); ++j) {
    for (size_t k = 0; k < jobs[j].size(); ++k) {
      const auto [machine, duration] = jobs[j][k];
      const IntVar s = model.NewIntVar(Domain(0, horizon));
      start[j].push_back(s);
      on_machine[machine].push_back(model.NewFixedSizeIntervalVar(s, duration));
      if (k > 0) {
        // The previous task of the same job must finish first.
        model.AddGreaterOrEqual(s, LinearExpr(start[j][k - 1]) + jobs[j][k - 1].second);
      }
    }
    if (!jobs[j].empty()) {
      const size_t last = jobs[j].size() - 1;
      model.AddGreaterOrEqual(makespan, LinearExpr(start[j][last]) + jobs[j][last].second);
    }
  }
  // One no-overlap per machine, over that machine's intervals only.
  for (const auto& intervals : on_machine) {
    if (!intervals.empty()) model.AddNoOverlap(intervals);
  }
  model.Minimize(makespan);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cerr << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  std::cout << "{\"start\": [";
  for (size_t j = 0; j < jobs.size(); ++j) {
    std::cout << (j ? ", " : "") << "[";
    for (size_t k = 0; k < jobs[j].size(); ++k) {
      std::cout << (k ? ", " : "") << SolutionIntegerValue(response, start[j][k]);
    }
    std::cout << "]";
  }
  std::cout << "]}\n";
  return 0;
}
