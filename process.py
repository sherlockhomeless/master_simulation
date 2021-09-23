from typing import List
from task import Task
from random import randint
import config


# --- CLASS ---
class Process:
    def __init__(self, tasks: List[Task], buffer: int):
        """
        Representation of a process on a node.
        Params:
            tasks: List of Tasks
            buffer: number of instructions from end of last task to deadline
            deadline: Deadline in instruction, counting from 0 at start
        """
        assert type(tasks[0]) is Task
        assert type(buffer) is int

        process_id = tasks[0].process_id
        self.process_id = process_id
        self.tasks = tasks

        # global
        self.log = config.LOG

        # config
        self.buffer = int(buffer)  # unedited, pure number of instructions that an process has until its deadline

        # state tracking
        self.instructions_executed = 1  # count of all instructions already done; set to 1 to prevent division by 0
        self.instructions_left = sum(tasks)  # instructions that are left according to plan
        self.instructions_planned = self.instructions_left
        self.process_length = self.instructions_left  # none changing amount of instructions
        self.number_tasks = len(tasks)  # number of all tasks of process
        self.threshold_state = 0  # 0 => no thresholds breaches, -2 => t_m2, 1/2 => t1/t2
        self.lateness = 0

        self.finished_process = False
        self.lateness_neutralizer: int = 0

    def __len__(self):
        return self.number_tasks

    def update_lateness(self):
        lateness_process = sum([t.get_lateness_task() for t in self.tasks])
        self.lateness = lateness_process + self.lateness_neutralizer
        self.instructions_executed += config.INS_PER_TICK

    def get_process_completion(self) -> float:
        """
        :return: process completion, 1 represents 100%
        """

        completion = self.instructions_planned / self.instructions_executed
        return min(completion, 1.0)

    @staticmethod
    def _generate_random_process(tasks=[], num_tasks=10, pid=0):
        """
        Static Method here to help Unittest testing
        :param tasks: list of tasks
        :param buffer: buffer
        :param deadline: deadline
        :return: random Process
        """
        if not tasks:
            for t in range(num_tasks):
                tasks.append(Task((randint(1, 10)*config.INS_PER_TICK), t, pid))
        return Process(tasks)

    def __repr__(self):
        return f"{{'process_id: {self.process_id}, 'lateness': {self.lateness}}}"

