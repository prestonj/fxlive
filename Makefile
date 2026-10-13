# fxlive against an octabam checkout. OCTABAM defaults to the directory you
# run make from if it is one, else ../octabam beside this repository; set it
# to point at a worktree:
#
#   make -C ~/git/fxlive OCTABAM=$PWD MODULE=MINIVERB
FXLIVE := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
OCTABAM ?= $(shell d="$(PWD)"; while [ "$$d" != / ]; do [ -f "$$d/tools/remix/schema.py" ] && { echo "$$d"; exit; }; d=$$(dirname "$$d"); done; echo "$(abspath $(FXLIVE)/../octabam)")
OCTABAM := $(abspath $(OCTABAM))
export OCTABAM
BUILD := $(OCTABAM)/out/fxlive/build
PY := $(OCTABAM)/.venv/bin/python3

.PHONY: run hosts check help
run: hosts ## Hear one effect live. [MODULE=KEY] [WAV=loop.wav] [REMIX= to override its host] [FXLIVEARGS=--port N|--device NAME|--no-audio]
	$(PY) $(FXLIVE)/fxlive.py $(if $(MODULE),--module "$(MODULE)") $(if $(REMIX),--remix "$(REMIX)") $(if $(WAV),--wav "$(WAV)") $(FXLIVEARGS)

check: hosts ## cf_host against Tape Echo's native oracle, and the stock DELAY's tempo law
	$(PY) $(FXLIVE)/check.py

hosts: ## Build dsp_host_stream and ot_cf_host from $(OCTABAM)'s sources (a no-op when current)
	@test -f "$(OCTABAM)/tools/remix/schema.py" || { echo "fxlive: $(OCTABAM) is not an octabam checkout; set OCTABAM="; exit 1; }
	@test -x "$(PY)" || { echo "fxlive needs $(OCTABAM)/.venv with numpy and sounddevice: make emu-setup there"; exit 1; }
	@test -f "$(BUILD)/CMakeCache.txt" || cmake -S "$(FXLIVE)" -B "$(BUILD)" -DOCTABAM="$(OCTABAM)" -DCMAKE_BUILD_TYPE=Release
	cmake --build "$(BUILD)" --target dsp_host_stream ot_cf_host -j8

help:
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'
	@echo "OCTABAM = $(OCTABAM)"
