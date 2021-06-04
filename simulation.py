#!/usr/bin/env python3
import sys
from typing import List

from process import Process
from plan import Plan
from task import Task
from process_runner import ProcessRunner
import config

# BUG: Task_id generation is completely fucked; task 0-n on p0, n+1-m on p1,...
# TODO: PLAN: Plan is getting reversed, so short processes start late
# TODO: Visualisierung durchschnittlicher Threshold
# TODO: Update Node Lateness


def run_sim(saved_plan=None):
    # if simulation should not run saved plan, create new
    if saved_plan is None:
        new_plan = Plan.generate_plan(file_path=config.WRITE_PLAN)
    else:
        new_plan = Plan.read_plan_from_file(saved_plan)

    runner = ProcessRunner(new_plan)
    Plan.write_plan_to_file(new_plan, config.WRITE_PLAN)

    print(f'Running simulation {new_plan}')
    while not runner.has_finished() and not config.JUST_WRITE_PLAN:
        runner.run_tick()


def create_processes(process_info: [List[Task], int]) -> List[Process]:
    """
    Creates processes according to the configuration given above.
    Process-Info is list of tuples [(<task-list>,buffer),...]
    """
    processes = []
    for p in process_info:
        # tasklist, buffer, deadline
        processes.append(Process(p[0], p[1]))
    return processes


if __name__ == '__main__':
    if len(sys.argv) == 1:
        run_sim(saved_plan="logs/plan.log")
    else:
        run_sim()
