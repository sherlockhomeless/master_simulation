from random import randint
import numpy as np

sigma = None

class Task:
    """
    Representation of a task of a process/job.
    The real length is determined by a random variable
    """
    def __init__(self, length_plan, process_id, task_id, length_real=None):
        global sigma
        assert type(length_plan) is int
        self.length_plan = length_plan # instructions left to process
        if length_real is None:
            self.length_real = int(np.random.normal(length_plan, length_plan/100*sigma, 1))
        else:
            self.length_real = length_real
        self.process_id = process_id
        self.task_id = task_id
        self.late = False
        self.task_finished = False

    def run(self, ins) -> int:
        '''
        Runs the task, returns 1 if the task hasn't finished and -n if it has finished.
        n is the amount of instructions that are left in the current tick
        '''
        self.length_real -= ins
        self.length_plan -= ins
        return self.length_real if self.length_real < 0  else 1

    def __str__(self):
        return f'(process: {self.process_id}, id: {self.task_id}, plan_len: {self.length_plan}, real_len:{self.length_real})'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return self.length_plan + other.length_plan

    def __radd__(self, other):
        return other + self.length_plan
