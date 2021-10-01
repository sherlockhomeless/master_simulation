#!/usr/bin/env python3

import sys

from plan import Plan
from process_runner import ProcessRunner
import config
import helper


def run_sim(saved_plan=None):
    """
    Starts a full run of the simulation
    :param saved_plan: Path to an existing plan; If none is given new plan is generated
    """
    if saved_plan is None:
        p = Plan.generate_plan(file_path=config.WRITE_PLAN)
        Plan.write_plan_to_file(p, config.WRITE_PLAN)
    else:
        p = Plan.read_plan_from_file(saved_plan)

    # Stretching plan or process for testing purposes, pid can be given to apply_stretch to only stretch one process
    stretch: float = 2.0  # no stretch
    p = helper.apply_stretch_real_length(p, stretch)
    runner = ProcessRunner(p)

    config.logger.info(f'Running simulation {p}')
    runner.run()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        config.logger.info(f'running simulation with plan {sys.argv[1]}')
        run_sim(saved_plan=sys.argv[1])
    else:
        run_sim()
