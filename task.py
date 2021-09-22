from random import randint
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

        assert type(length_plan) is int
        self.length_plan_unchanged = length_plan
        self.length_plan: int = length_plan  # decreases
        self.instruction_counter = InstructionTracker()
        if length_real is None:
            possible_reals = np.random.normal(length_plan, length_plan/100 * config.TASK_SIGMA, 100)
            self.length_real = int(possible_reals[randint(0, 99)])
        else:
            self.length_real = int(length_real)
        self.process_id = process_id
        self.task_id = task_id

        self.task_finished = False
        self.is_running = False
        self.finished_early = False
        self.finished_late = False
        self.finished_on_time = False
        self.is_late = False
        self.was_preempted: int = 0  # counter for the amount of preemptions
        self.was_signaled: PredictionFailureSignal = None

        # Reference to other tasks in which slot self was inserted too
        # The order is (firstly inserted task, secondly inserted task,...)
        self.shares_slot_with = []
        self.shares_slot = False
        self.t1_data = None

    def run(self, ins):
        """
        Runs the task, returns 1 if the task hasn't finished and -n if it has finished.
        n is the amount of instructions that are left in the current tick
        """
        assert type(ins) is int
        # --- instructions counting ---
        self.length_real -= ins
        self.length_plan -= ins
        self.instruction_counter.run_instructions_task(ins)

        assert type(self.length_plan) is int

        # --- state checks ---
        if self.length_real <= 0:
            self.task_finished = True
            if self.length_plan > 0 and self.was_preempted == 0:
                self.finished_early = True
            elif self.length_plan < 0 or self.was_preempted > 0:
                self.finished_late = True
            else:
                self.finished_on_time = True
        else:
            self.is_running = True
            if self.length_plan <= 0:
                self.is_late = True

        # assign run instructions to slot
        if not self.was_preempted:
            self.instruction_counter.run_instructions_slot(ins)
        else:
            self.shares_slot_with[-1].instruction_counter.run_instructions_slot(ins)

        assert self.length_real >= 0 or self.task_finished

    def has_task_finished(self):
        return self.task_finished

    def has_task_finished_early(self):
        return self.finished_early

    def is_task_late(self):
        return self.is_late

    def get_lateness_task(self) -> int:
        """
        Returns Lateness of Task:
        If the task has finished or task is late: retired_instructions - length_plan
        else: 0
        :return:
        """
        if self.has_task_finished() or self.is_task_late():
            return self.instruction_counter.instructions_task - self.length_plan_unchanged
        else:
            return 0

    def get_overdone_instructions(self):
        """
        If a task has finished, it has to return the amount of instructions it has overdone so those can be added to another task
        """
        assert self.length_real <= 0
        return -self.length_real

    def get_late_instructions(self, ins) -> int:
        """
        Helper method, that helps get the instructions a Task is late. Helps to decide if all instructions of a tick add to lateness or just some part of them
        """
        return -self.length_plan if self.turned_late else ins

    def get_early_instructions(self, unused_instructions=0):
        """
        : param unused_instructions: int
        Helper method that helps get keeps track of instructions, if a task finished early.
        """
        assert self.length_real < self.length_plan
        assert self.finished_early is True
        return -self.length_plan

    def set_times(self, cur_time) -> int:
        """
        Sets the start and endtime of the current task, returns the planned endtime
        """
        self.start_time = cur_time
        self.end_time = cur_time + self.length_plan
        return self.end_time

    def get_instructions_cur_slot(self):
        """
        Returns the instructions that were run inside the slot the current task is assigned to
        :return:
        """
        if not self.was_preempted:
            return self.instruction_counter.instructions_slot
        else:
            return self.shares_slot_with[-1].instruction_counter.instructions_slot

    def preempt(self, other_task: 'Task'):
        """
        Self was preempted and now shares a slot with another Task, Informations on self have to updated to calculate t1 accordingly
        :param other_task: Task self was inserted before
        """
        assert other_task.process_id == self.process_id
        assert other_task is not self
        self.is_running = False
        # share information with other tasks that had to share their slot
        if len(self.shares_slot_with) > 0 and self.shares_slot_with[0].shares_slot:
            self.shares_slot_with[0].preempt(other_task)

        self.shares_slot_with.append(other_task)
        other_task.shares_slot = True

    def signal(self, sig: "PredictionFailure"):
        """
        This Task was signaled
        :return:
        """
        self.was_signaled = sig

    def __str__(self):
        return f"{{'task_id': {self.task_id}, 'process': {self.process_id}, 'plan_len': {self.length_plan}, " \
               f"'real_len': {self.length_real}, 'lateness_task': {self.get_lateness_task()}}}"

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        assert type(other) is Task
        return self.length_plan_unchanged + other.length_plan_unchanged

    def __radd__(self, other):
        return other + self.length_plan_unchanged

    @staticmethod
    def get_placeholder_task() -> "Task":
        return Task(-1, -1, -1)
