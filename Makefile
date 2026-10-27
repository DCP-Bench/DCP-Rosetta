# The commands this repository is run with. `make` alone lists them.
# Every target is a thin wrapper: the command it runs is the one the README,
# the CI workflows and the skills document, so either form can be used.

PYTHON ?= python
RUFF ?= ruff
PORT ?= 8000
# For the targets that act on one problem, integration or model.
PROBLEM ?=
SOLVER ?=
MODEL ?=
LIMIT ?= 20

DATASET := bench/dcp-bench-open.jsonl
# The conversion solves every reference model (about 20 s), so the jsonl is
# rebuilt only when a problem file or the converter is newer than it.
DATASET_SOURCES := $(shell find bench/dataset -type f 2>/dev/null) bench/jsonl_convert.py
# Where an integration lives, `solvers/<solver>/<interface>/`, read from its ID.
FOLDER = $(shell $(PYTHON) -c "from evaluation.execution import integration_folder; print(integration_folder('$(SOLVER)').relative_to(__import__('pathlib').Path.cwd()))")

.DEFAULT_GOAL := help
.PHONY: help install dataset site serve clean test test-containers test-all dataset-audit \
	lint validate-skills build readiness readiness-verify next-work brief check eval-sample \
	instances-status

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  \033[1m%-18s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  Variables: PROBLEM=, SOLVER= (an integration ID, e.g. choco_java), MODEL=, PORT=$(PORT), LIMIT=$(LIMIT)"

# ---- Setup -----------------------------------------------------------------

install: ## Install the Python requirements (Python 3.12)
	$(PYTHON) -m pip install -r requirements.txt

$(DATASET): $(DATASET_SOURCES)
	cd bench && $(PYTHON) jsonl_convert.py

dataset: ## Rebuild bench/dcp-bench-open.jsonl from bench/dataset/, even when it looks current
	cd bench && $(PYTHON) jsonl_convert.py

# ---- Website ---------------------------------------------------------------

site: $(DATASET) ## Build the catalogue website into site/
	$(PYTHON) generate_site.py

serve: site ## Build the website and serve it on localhost (PORT=)
	$(PYTHON) -m http.server $(PORT) --directory site

clean: ## Remove the built website
	rm -rf site

# ---- Tests and checks ------------------------------------------------------

test: ## Run the tests that need no Docker
	$(PYTHON) -m unittest tests.test_evaluation tests.test_generation tests.test_skill_workflow \
		tests.test_readiness tests.test_site

test-containers: ## Run the tests against the built solver images (needs Docker and `make build`)
	$(PYTHON) -m unittest tests.test_solvers tests.test_generation_containers

test-all: ## Run every test under tests/
	$(PYTHON) -m unittest discover -s tests -t .

dataset-audit: ## Audit the problems in bench/
	cd bench && $(PYTHON) -m unittest tests.test_dataset

lint: ## Lint with ruff
	$(RUFF) check .

validate-skills: ## Validate the project skills under skills/
	for skill in skills/*/; do $(PYTHON) -m generation.skills validate $${skill%/} --project >/dev/null || exit 1; done

# ---- Evaluation ------------------------------------------------------------

build: ## Build the solver images (all, or SOLVER=id); needs Docker
	$(PYTHON) -m evaluation.build $(SOLVER)

readiness: ## Run SOLVER's readiness checks and record them, after a build
	@test -n "$(SOLVER)" || { echo "Set SOLVER=<integration id>"; exit 2; }
	$(PYTHON) -m generation.readiness check --solver $(SOLVER) --output $(FOLDER)/readiness.json

readiness-verify: ## Verify SOLVER's readiness record still matches its image
	@test -n "$(SOLVER)" || { echo "Set SOLVER=<integration id>"; exit 2; }
	$(PYTHON) -m generation.readiness verify --solver $(SOLVER) --record $(FOLDER)/readiness.json

check: ## Evaluate one model: MODEL=path PROBLEM=id SOLVER=id
	@test -n "$(MODEL)" -a -n "$(PROBLEM)" -a -n "$(SOLVER)" || { echo "Set MODEL=, PROBLEM= and SOLVER="; exit 2; }
	$(PYTHON) -m evaluation.check --problem $(PROBLEM) --solver $(SOLVER) $(MODEL)

# Four of the five are wrong on purpose, so eval.py's failing exit is expected.
eval-sample: $(DATASET) ## Check sample_test.jsonl's five models with CPMpy
	-$(PYTHON) eval.py --dataset_file $(DATASET) --test_file sample_test.jsonl --modelling_framework CPMpy

# ---- Model generation ------------------------------------------------------

next-work: ## List the work left: usable integrations and unmodelled pairs (LIMIT=)
	$(PYTHON) -m generation.next_work --limit $(LIMIT)

brief: ## Print what a model of PROBLEM has to satisfy
	@test -n "$(PROBLEM)" || { echo "Set PROBLEM=<problem id>"; exit 2; }
	$(PYTHON) -m generation.brief $(PROBLEM)

instances-status: ## List the problems that can take more instances
	$(PYTHON) -m generation.instances status
