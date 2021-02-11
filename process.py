from typing import List
from task import Task
from random import randint
import config


# --- CLASS ---
class Process:
    def __init__(self, tasks: List[Task], buffer: int, deadline: int):
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

        # global
        self.log = config.LOG

        # config
        self.buffer = int(buffer)  # unedited, pure number of instructions
        self.deadline = int(deadline)

        # state tracking
        self.instructions_executed = 0
        self.instructions_left = sum(tasks)
        self.number_tasks = len(tasks)
        self.threshold_state = 0  # 0 => no thresholds breaches, -2 => t_m2, 1/2 => t1/t2

        self.finished_process = False

    def __len__(self):
        return self.number_tasks

    @staticmethod
    def _generate_random_process(tasks=[], buffer=1,deadline=1, num_tasks=10, pid=0):
        """
        Static Method here to help Unittest testing
        :param tasks: list of tasks
        :param buffer: buffer
        :param deadline: deadline
        :return: random Process
        """
        if not tasks:
            for t in range(num_tasks):
                tasks.append(Task((randint(1,10)*config.INS_PER_TICK), t, pid))
        return Process(tasks)


