PYTHON = python3

help:
	@echo ""
run_vis:
	${PYTHON} simulation.py logs/plan.log && cd visualization && python3 vis.py
run-new:
	${PYTHON} simulation.py run-with-new
