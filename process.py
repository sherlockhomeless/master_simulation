from typing import List
from task import Task

ipt = None  # instructions per tick
load = None
log = False
hz = None
max_buff_usg = 0
ticks_off = 1
max_task_deviation = None
# depending on the general lateness on the node, this value will be adjusted
max_task_overstep = None


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
        # global
        self.load = load  # systemload
        self.hz = hz
        self.ipt = ipt
        self.log = log
        self.max_buff_usg = max_buff_usg

        # config
        self.buffer = buffer  # unedited, pure number of instructions
        self.deadline = int(deadline)

        # state keeping process
        self.tasks_plan = tasks  # list of all tasks
        self.cur_task = self.tasks_plan[0]  # currently running task
        # the originally tracked length of the current task
        self.cur_task_length_plan = self.cur_task.length_plan
        self.process_id = self.cur_task.process_id
        self.finished_process = False

    def run_task(self, task_id, ins):
        '''
        updates the state of the task list
        ! Assumes that the instructions given already account for switching of Tasks, e.g. if a Task is finished and the next one is started within one tick, that the instructions per Tick are correctly distributed, no futher checks are made here
        '''
        def task_finished() -> bool:
            if self.cur_task.length_real <= 0:
                assert ins == self.cur_task.length_real
                return True
            else:
                return False

        def move_to_next_task():
            self.tasks_plan = self.tasks_plan[1:]  # move to next task
            if len(self.tasks_plan) == 0:  # process has finished
                self.finished_process = True
                return
            self.cur_task = self.tasks_plan[0]  # pick next task
            self.cur_task_length_plan = self.cur_task.length_plan  # set variable

        if task_finished() is True:
            move_to_next_task()

    # def update_lateness(self):
    #     # task is on time
    #     if self.cur_task.length_plan > 0:
    #         return
    #     # tasks turns late
    #     elif self.cur_task.length_plan < 0 and self.cur_task.late is False:
    #         self.lateness_task += self.cur_task.length_plan
    #         self.lateness_process += self.cur_task.length_plan
    #         self.cur_task.late = True
    #     elif self.cur_task.length_plan < 0 and self.cur_task.late is True:
    #         self.lateness_task += self.ipt
    #         self.lateness_process += self.ipt

    def __len__(self):
        return len(self.tasks_plan)

    def update_stress(self, change: int):
        pass  # TODO: implement; change max_task_overstep
