#!/usr/bin/env python3

import sys

from plan import Plan
from process_runner import ProcessRunner
import config
import helper

# BUG: Task_id generation is completely fucked; task 0-n on p0, n+1-m on p1,...
# TODO: PLAN: Plan is getting reversed, so short processes start late
# TODO: Update Node Lateness


def run_sim(saved_plan=None):
    # if simulation should not run saved plan, create new
    if saved_plan is None:
        p = Plan.generate_plan(file_path=config.WRITE_PLAN)
        Plan.write_plan_to_file(p, config.WRITE_PLAN)
    else:
        p = Plan.read_plan_from_file(saved_plan)

    stretch: float = 1.0  # no stretch
    p = helper.apply_stretch_to_process(p, stretch)  # If wanted, pid can be passed as kwarg
    runner = ProcessRunner(p)

    config.logger.info(f'Running simulation {p}')
    if not config.JUST_WRITE_PLAN:
        runner.run()

    for finished_task in runner.finished_tasks:
        assert finished_task.has_task_finished() is True


if __name__ == '__main__':
    if len(sys.argv) == 2:
        config.logger.info(f'running simulation with plan {sys.argv[1]}')
        run_sim(saved_plan=sys.argv[1])
    else:
        run_sim()
