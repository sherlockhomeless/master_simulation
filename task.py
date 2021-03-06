from __future__ import annotations

from random import randint
from typing import Optional
import numpy as np

from job_scheduler import PredictionFailureSignal
from instruction_counter import InstructionTracker
import config


class Task:
    """
    Representation of a task of a process/job.
    The real length is determined by a random variable
    """

    def __init__(self, length_plan: int, process_id: int, task_id: int, length_real=None):
        assert type(length_plan) is int

        self.process_id = process_id
        self.task_id = task_id

        self.task_finished = False
        self.is_running = False
        self.finished_early = False
        self.finished_late = False
        self.finished_on_time = False
        self.was_preempted: int = 0  # counter for the amount of preemptions
        self.was_signaled: Optional[PredictionFailureSignal] = None

        self.times_preempted: int = 0
        self.slot: Task = self

        if length_real is None:
            possible_reals = np.random.normal(length_plan, length_plan/100 * config.TASK_SIGMA, 100)
            self.length_real = int(possible_reals[randint(0, 99)])
        else:
            self.length_real = int(length_real)

        self.instructions = InstructionTracker(instructions_planned=length_plan, instructions_real=self.length_real)

    def run(self, ins):
        """
        :param ins: Amount of instructions task is supposed to run
        """
        assert type(ins) is int
        # --- instructions counting ---
        self.instructions.instructions_retired_task += ins
        self.slot.instructions.instructions_retired_slot += ins

        # --- state checks ---
        if self.instructions.has_finished():
            self.task_finished = True
            if self.instructions.has_finished_early():
                self.finished_early = True
            elif self.instructions.is_late():
                self.finished_late = True
            else:
                self.finished_on_time = True
        else:
            self.is_running = True

    def has_task_finished(self):
        return self.task_finished

    def has_task_finished_early(self):
        return self.finished_early

    def is_task_late(self):
        return self.instructions.is_late()

    def get_lateness_task(self) -> int:
        return self.instructions.get_lateness()

    def get_overdone_instructions(self):
        """
        If a task has finished, it has to return the amount of instructions so they can be considered by the simulation
        """
        assert self.instructions.instructions_retired_task >= self.instructions.real
        return self.instructions.real - self.instructions.instructions_retired_task

    def get_instructions_cur_slot(self):
        """
        Returns the instructions that were run inside the slot the current task is assigned to
        :return:
        """
        return self.slot.instructions.instructions_retired_slot

    def preempt(self, other_task: Task):
        """
        * sets the new next slot for self and all other tasks that self was inserted before
        :param other_task: Task self was inserted before
        """
        assert other_task.process_id == self.process_id
        assert other_task is not self

        self.is_running = False
        self.was_preempted = True

        self.times_preempted += 1

        self.slot = other_task.slot

    def signal(self, sig: PredictionFailureSignal):
        """
        This Task was signaled
        :return:
        """
        self.was_signaled = sig

    def get_current_slot_owner(self) -> Task:
        """
        The shares_slot_with list contains all the tasks in which slots self was inserted to
        :return:
        """
        return self.slot

    def __str__(self):
        return f"'task_id': {self.task_id}, 'process': {self.process_id}, 'plan_len': " \
               f"{self.instructions.plan}, " \
               f"'real_len': {self.length_real}, 'lateness_task': {self.get_lateness_task()}}}"

    def __repr__(self):
        return self.__str__()

    def __add__(self, other: Task):
        assert type(other) is Task
        return self.instructions.plan + other.instructions.plan

    def __radd__(self, other: Task):
        return other + self.instructions.plan

    @staticmethod
    def get_placeholder_task() -> "Task":
        return Task(-1, -1, -1)
