from pudb import set_trace

from process import Process
from task import Task

log = False
reschedule_time = None  # time it takes to receive a new plan
max_task_deviation_t1_t1 = None  # Max. Insrtructions a Task is allowed to be off
max_relative_deviation_t1 = None # Max relative deviation for t1
ipt = None
cap_lateness = None
consumable_buffer = None
spacer_constant = None


class Threshold:
    def __init__(self, process: Process):
        # --- Config ---
        self.process = process
        self.process_id = process.process_id
        self.reschedule_time = reschedule_time
        self.ipt = ipt
        # how much is a task allowed to deviate from it's plan, eg. 120% => 1.2
        self.CAP_LATENESS = cap_lateness
        # how much of the buffer is available for usage
        self.CONSUMEABLE_BUFFER = consumable_buffer
        # factor that determines how much bigger t2 has to be then t1
        self.SPACER_CONSTANT = spacer_constant
        # counted in number of instructions off globaly max off
        self.max_task_deviation_t1 = max_task_deviation_t1
        # given in % of task planned length
        self.max_relative_deviation_t1 = max_relative_deviation_t1
        # [TODO] Include Load
        self.load = 1
        # [CHECK] Total available buffer in instructions
        self.buffer = process.buffer
        self.deadline = process.deadline
        self.reschedule_time = reschedule_time
        self.threshold_state = 0  # holds the current state of the threshold

        self.t1 = None
        self.t2_task = None
        self.t2_process = None
        self.t_minus2 = None

        self.thresholds = {
            "t1": self.t1,
            "t2_task": self.t2_task,
            "t2_process": self.t2_process,
            "t_minus2": self.t_minus2,
            "t1_pure": 0,
            "t2_pure": 0,
            "t_minus2_pure": 0
        }

        # --- admin ---
        self.log = log
        self.thresh_flag = None
        self.log_thresh = open(f'logs/thresh_{self.process_id}.log', 'w')
        # logging of the pure instruction amount that is been granted
        self.log_thresh_pure = open(f'logs/pure_{self.process_id}.log', 'w')

    def update_thresholds(self, instructions_left: int, instructions_planned: int, cur_task: Task, stress=1, load=1):
        """
        Sets the Thresholds
        [TODO]: Include stress calculation
        """

        usable_buffer = self.calc_usable_buffer(instructions_planned, instructions_left)
        self.t1 = self.calc_t1(cur_task.length_plan_unchanged)
        self.t2 = self.calc_t2(usable_buffer, cur_task.length_plan_unchanged)
        self.t_minus2 = self.calc_t_minus(cur_task.length_plan)

        try:
            assert self.t1 < self.t2
            assert 0 < self.t1 and 0 < self.t2
            assert self.t_minus2 < 0
        except AssertionError:
            print("assertion error in update_thrsholds")
        self.update_dict(instructions_planned)

        if self.log is True:
            self.log_thresh.write(
                f'{cur_task.task_id} {self.t1} {self.t2} {self.t_minus2}\n')
            self.log_thresh_pure.write(
                f'{cur_task.task_id} {self.t1 - cur_task.length_plan} {self.t2 - cur_task.length_plan} {self.t_minus2}\n')

    def calc_t1(self, instructions_planned) -> int:
        '''
        Calculates the t1 at which the currently running task is preempted and replaced by the next task in the plan.
        t1 is the minimum off two values, one of which represents an absolute boundary, the other a relative boundary:

            * max_global_deviation => is a global boundary that ensures that independant of the task details, a certain amount of ticks is not transgressed
            * max_local_deviation => is a local, relative boundary relating to the details of the task TODO: AND PROCESS
        '''
        max_global_deviation = self.max_task_deviation_t1 + instructions_planned
        max_local_deviation = instructions_planned * self.max_relative_deviation_t1
        t1 = int(min(max_global_deviation, max_local_deviation))
        #  print("max_global_deviation") if max_global_deviation < max_local_deviation else print("max_local_deviation")

        return t1

    def calc_t2(self, available_buffer, length_plan, stress=0) -> int:
        """
        Triggers PredictionFailure to VRM. Conditions:
        1. Individual Task was extremly off => in current implementation this condition holds if one task takes the amount of two slots of the assigned time
        2. Whole Process is off by significant amount proportional to state of progress

        [TODO] static threshhold depending on stress level
        """

        t2_with_buffer_cap = self.t1 + stress * self.ipt - self.reschedule_time
        t2_cap_lateness = self.CAP_LATENESS * length_plan
        t2 = min(t2_with_buffer_cap, t2_cap_lateness)
        t2 = int(t2)

        return t2 if t2 > self.t1 else self.t1 * self.SPACER_CONSTANT

    def calc_t_minus(self, instructions_planned):
        return int(-1 * self.t2 * 2)

    def get_thresholds(self) -> dict:
        return self.thresholds

    def calc_usable_buffer(self, instructions_planned, instructions_left):
        """
        Calculates the proportion of the buffer that is allowed to be used up
        """
        instructions_done = instructions_planned - instructions_left
        process_completion = instructions_done / instructions_planned
        available_buffer = self.buffer * self.load * self.CONSUMEABLE_BUFFER
        usable_buffer = available_buffer * process_completion

        assert usable_buffer < available_buffer
        assert usable_buffer >= 0  # t2 with 0% completion should just be one of other thresholds

        return int(usable_buffer)

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

    def update_dict(self, ins_planed: int):
        self.thresholds['t1'] = self.t1
        self.thresholds['t2'] = self.t2
        self.thresholds['t_minus2'] = self.t_minus2
        self.thresholds['t1_pure'] = self.t1 - ins_planed
        self.thresholds['t2_pure'] = self.t2 - ins_planed
        self.thresholds['t_minus2_pure'] = self.t1 + ins_planed

    def __getitem__(self, name):
        return self.thresholds[name]

    @staticmethod
    def setup_for_testing(max_task_dev, ins_per_sec):
        """
        : param max_task_dev: int, max instructions
        : param ins_per_sec: int, regular ipt
        """

        log = False
        ipt = ins_per_sec
        reschedule_time = 0  # time it takes to receive a new plan
        max_task_deviation_t1 = max_task_dev   # Max. Insrtructions a Task is allowed to be off
        max_relative_deviation_t1 = None
        cap_lateness = None
        consumable_buffer = None
        spacer_constant = None
