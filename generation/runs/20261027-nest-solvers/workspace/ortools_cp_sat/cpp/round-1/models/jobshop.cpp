// Job-shop scheduling: minimise the makespan. One AddNoOverlap per machine.
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
  // jobs[j][k] = {machine, duration}
  const auto jobs =
      instance.at("jobs").get<std::vector<std::vector<std::pair<int, int64_t>>>>();

  int num_machines = 0;
  int64_t horizon = 0;
  for (const auto& job : jobs) {
    for (const auto& [machine, duration] : job) {
      num_machines = std::max(num_machines, machine + 1);
      horizon += duration;
    }
  }

  CpModelBuilder model;
  std::vector<std::vector<IntVar>> start(jobs.size());
  std::vector<std::vector<IntervalVar>> on_machine(num_machines);
  for (size_t j = 0; j < jobs.size(); ++j) {
    for (size_t k = 0; k < jobs[j].size(); ++k) {
      const auto [machine, duration] = jobs[j][k];
      start[j].push_back(model.NewIntVar(Domain(0, horizon - duration)));
      on_machine[machine].push_back(model.NewFixedSizeIntervalVar(start[j][k], duration));
      if (k > 0) {
        model.AddGreaterOrEqual(start[j][k], start[j][k - 1] + jobs[j][k - 1].second);
      }
    }
  }
  for (const auto& intervals : on_machine) model.AddNoOverlap(intervals);

  IntVar makespan = model.NewIntVar(Domain(0, horizon));
  for (size_t j = 0; j < jobs.size(); ++j) {
    const size_t last = jobs[j].size() - 1;
    model.AddGreaterOrEqual(makespan, start[j][last] + jobs[j][last].second);
  }
  model.Minimize(makespan);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  nlohmann::json out;
  out["start"] = nlohmann::json::array();
  for (const auto& job_starts : start) {
    nlohmann::json row = nlohmann::json::array();
    for (const IntVar& s : job_starts) row.push_back(SolutionIntegerValue(response, s));
    out["start"].push_back(row);
  }
  std::cout << out.dump() << "\n";
  return 0;
}
