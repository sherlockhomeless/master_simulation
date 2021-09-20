PYTHON = python3

run_vis:
	${PYTHON} simulation.py logs/plan.log && cd visualization && python3 vis.py
run:
	${PYTHON} simulation.py logs/plan.log
run_new:
	${PYTHON} simulation.py
