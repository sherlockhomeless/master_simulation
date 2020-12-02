from process import Process
from task import Task

log = False
reschedule_time = None # time it takes to receive a new plan
max_task_deviation = None # Max. Insrtructions a Task is allowed to be off



class Threshold:
    def __init__(self, process: Process):
        # --- Config ---
        self.process = process
        self.process_id = process.process_id
        self.reschedule_time = reschedule_time
        self.max_task_deviation = max_task_deviation # counted in number of instructions

        self.buffer = process.buffer
        self.deadline = process.deadline
        self.reschedule_time = reschedule_time
        self.threshold_state = 0 # holds the current state of the threshold

        self.t1 = None
        self.t2 = None
        self.t_minus2 = None

        self.thresholds = {
        "t1": self.t1,
        "t2": self.t2,
        "t_minus2": self.t_minus2
        }

        # --- admin ---
        self.log = log
        self.thresh_flag = None
        self.log_thresh = open(f'logs/thresh_{self.process_id}.log', 'w')
        self.log_thresh_pure = open(f'logs/pure_{self.process_id}.log', 'w') # logging of the pure instruction amount that is been granted


    def update_thresholds(self, instructions_left: int, instructions_planned: int, cur_task: Task):
        """
        Sets the Thresholds
        """

        buffer_allowence = instructions_left/instructions_planned * self.buffer #* self.load TODO: Include Load
        self.t1 = self.calc_t1(cur_task.length_plan_unchanged)
        self.t2 = self.calc_t2(buffer_allowence)
        self.t_minus2 = self.calc_t_minus(cur_task.length_plan)

        if self.log is True:
            self.log_thresh.write(f'{cur_task.task_id} {self.t1} {self.t2} {self.t_minus2}\n')
            self.log_thresh_pure.write(f'{cur_task.task_id} {self.t1 - cur_task.length_plan} {self.t2 - cur_task.length_plan} {self.t_minus2}\n')

    def calc_t1(self, instructions_planned) -> int:
        '''
        Calculates the t1 at which the currently running task is preempted and replaced by the next task in the plan.
        t1 is the minimum off two values, one of which represents an absolute boundary, the other a relative boundary:

            * max_global_deviation => is a global boundary that ensures that independant of the task details, a certain amount of ticks is not transgressed
            * max_local_deviation => is a local, relative boundary relating to the details of the task TODO: AND PROCESS
        '''
        max_global_deviation = self.max_task_deviation + instructions_planned
        max_local_deviation = instructions_planned + self.max_task_deviation
        t1 = int(min(max_dev, max_overreach))
        print("max_dev") if max_dev < max_overreach else print("max_overreach")

        assert t1 > 0

        return t1

    def calc_t2(self, buffer_allowence) -> int:
        """
        Triggers PredictionFailure to VRM. Conditions:
        1. Individual Task was extremly off => in current implementation this condition holds if one task takes the amount of two slots of the assigned time
        2. Whole Process is off by significant amount proportional to state of progress

        TODO: static threshhold depending on stress level
        """

        condition1 = None # TODO

        allowence_relative = int(self.t1 + buffer_allowence - self.reschedule_time)
        condition2 = self.t1 + buffer_allowence - self.reschedule_time

        return min(allowence_relative, condition2)

    def calc_t_minus(self, instructions_planned):
        return int(-1 * self.t2 * 2)


    def get_thresholds(self) -> dict:
        return self.thresholds

    def check_thresholds(self) -> int:
        if self.lateness_task < self.t1:
            return 0
        elif self.lateness_task > self.t1:
            return 1
        elif self.lateness_process > self.t2:
            return 2
        else:
            return -1

    def __repr__(self):
        return f'process {self.process_id}: t1: {self.t1}, t2: {self.t2}, t_minu2: {self.t_minus2}'

    def __getitem__(self, name):
        return self.thresholds[name]
