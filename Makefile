# Makefile for dev environment

# Configuration ---------------------------------------------------------------
VENV = .venv
MODULES = client common load-balancer server
# -----------------------------------------------------------------------------

PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
REQS = $(patsubst %, ./%/requirements.txt, $(MODULES))

# Load venv
init: $(VENV)/bin/activate

# Clean environment
clean:
	docker compose down
	rm -rf **/__pycache__
	rm -rf $(VENV)

docker:
	docker compose up --build --force-recreate -d

# Setup python venv
$(VENV)/bin/activate: $(REQS)
	python3 -m venv $(VENV)
	$(PIP) install $(patsubst %, -r %, $(REQS))

.PHONY: default
default: init
# Make requirement.txt if it doesn't exist
$(REQS):
	touch $@ || exit
