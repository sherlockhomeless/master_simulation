import numpy as np
import config


class Task:
    """
    Representation of a task of a process/job.
    The real length is determined by a random variable
    """

    def __init__(self, length_plan, process_id, task_id, length_real=None):
        assert type(length_plan) is int

        self.length_plan_unchanged = length_plan
        self.length_plan = length_plan  # decreases
        self.run_instructions = 0  # increases
        if length_real is None:
            self.length_real = int(np.random.normal(
                length_plan, length_plan/100 * config.task_sigma, 1))
        else:
            self.length_real = length_real
        self.process_id = process_id
        self.task_id = task_id

        self.task_finished = False
        self.finished_early = False
        self.turned_late = False
        self.is_late = False
        self.was_preempted = False

    def run(self, ins):
        '''
        Runs the task, returns 1 if the task hasn't finished and -n if it has finished.
        n is the amount of instructions that are left in the current tick
        TODO: In real implementation => here only tick granularity is possible
        '''
        self.length_real -= ins
        self.length_plan -= ins
        self.run_instructions += ins

        if self.length_real <= 0:
            self.task_finished = True

        if self.length_plan < 0 and not self.task_finished:
            if self.is_late is False:
                self.turned_late = True
            else:
                self.turned_late = False
            self.is_late = True

        if self.task_finished and self.length_plan > 0:
            self.finished_early = True

    def has_task_finished(self):
        return self.task_finished

    def has_task_finished_early(self):
        return self.finished_early

    def is_task_late(self):
        return self.turned_late or self.is_late

    def get_overdone_instructions(self):
        """
        If a task has finished, it has to return the amount of instructions it has overdone so those can be added to another task
        """
        assert self.length_real <= 0
        return -(self.length_real)

    def get_late_instructions(self, ins) -> int:
        """
        Helper method, that helps get the instructions a Task is late. Helps to decide if all instructions of a tick add to lateness or just some part of them
        """
        return -(self.length_plan) if self.turned_late else ins

    def get_early_instructions(self, unused_instructions=0):
        """
        : param unused_instructions: int
        Helper method that helps get keeps track of instructions, if a task finished early.
        """
        assert self.length_real < self.length_plan
        return self.length_plan - (self.length_real - unused_instructions)

    def __str__(self):
        return f'(process: {self.process_id}, id: {self.task_id}, plan_len: {self.length_plan}, real_len:{self.length_real})'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return self.length_plan + other.length_plan

    def __radd__(self, other):
        return other + self.length_plan
