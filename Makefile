PYTHON = python3

help:
	@echo ""
run:
	${PYTHON} sim.py
vis:
	${PYTHON} vis.py
runvis: run vis
