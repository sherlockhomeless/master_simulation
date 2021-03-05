from pudb import set_trace

from process import Process
from task import Task
import config


reschedule_time = None  # time it takes to receive a new plan
max_ticks_off_t1 = None  # max time ticks a task is allowed to be off its plan
max_relative_deviation_t1 = None # sigma in thesis, % deviation from plan
ipt = None
cap_lateness = None
consumable_buffer = None
spacer_constant = None


class Threshold:
    # --- Config ---
    itp = config.INS_PER_TICK
    rescheduling_time = config.RESCHEDULE_TIME
    # --- PARAS t1 ---
    sigma_t1 = config.SIGMA_T1
    preempt_limit = config.PREEMPTION_LIMIT
    # --- PARAS t2 ---
    # how much of the buffer is available for usage
    consumable_buffer = config.ASSIGNABLE_BUFFER
    # how much is a task allowed to deviate from it's plan, eg. 120% => 1.2
    cap_lateness = config.CAP_LATENESS
    # factor that determines how much bigger t2 has to be then t1
    spacer_constant = config.T2_SPACER
    max_preemptions = config.T2_MAX_PREEMPTIONS

    @staticmethod
    def calc_t1(instructions_planned) -> int:
        '''
        Calculates the t1 at which the currently running task is preempted and replaced by the next task in the plan.
        t1 is the minimum off two values, one of which represents an absolute boundary, the other a relative boundary:

            * max_global_deviation => is a global boundary that ensures that independant of the task details, a certain amount of ticks is not transgressed
            * max_local_deviation => is a local, relative boundary relating to the details of the task TODO: AND PROCESS
        '''
        t1_relative_deviation = instructions_planned * config.SIGMA_T1
        t1_preemption_minimum = instructions_planned + config.NO_PREEMPTION
        relative_t1 = max(t1_relative_deviation, t1_preemption_minimum)

        t1 = int(min(relative_t1, Threshold.preempt_limit))

        return t1

    @staticmethod
    def calc_t2(buffer: int, instructions_planned_task: int, instructions_done_process: int,
                instructions_sum_process: int, t1: int, number_preemptions: int,  stress=0, load_free=1) -> int:
        """
        :param buffer: buffer given by the VRM
        :param instructions_planned_task: sum of all instructions of a process
        :param instructions_done_process: sum of all already executed instructions
        :param instructions_sum_process: sum of all planned task instructions
        :param t1: current calculated t1
        :param stress: system level stress factor
        :param number_preemptions: Amount of preemptions that ocured already
        :param load_free: Percentage of unallocated time on node

        Triggers PredictionFailure to VRM. Conditions:
        1. Individual Task was extremly off => in current implementation this condition holds if one task takes the amount of two slots of the assigned time
        2. Whole Process is off by significant amount proportional to state of progress

        [TODO] static threshhold depending on stress level
        """
        # --- sanitation ---

        if instructions_done_process == 0:
            instructions_done_process = 1

        available_buffer = buffer * load_free * config.ASSIGNABLE_BUFFER
        usable_buffer = available_buffer * (instructions_sum_process/instructions_done_process)

        t2_buffer_cap = t1 + usable_buffer + (stress * config.INS_PER_TICK) - config.RESCHEDULE_TIME
        t2_relative = instructions_planned_task * config.CAP_LATENESS
        t2_spacer = t1 + config.T2_SPACER

        t2_task = max(t2_relative, t2_spacer)
        t2_task_capped = min(t2_task, t2_buffer_cap)

        # [TODO]: Implement
        t2_process = t2_task_capped

        t2 = min(t2_process, t2_task_capped)

        assert t1 < t2

        # if a task is interrupted too often, a prediction failure must occur
        if number_preemptions >= Threshold.max_preemptions:
            t2 = 0
        return int(t2)

    @staticmethod
    def calc_t_minus(t2):
        # [TODO]: Implement
        return int(-1 * t2 * 2)

    @staticmethod
    def calc_usable_buffer(instructions_planned, instructions_left, buffer=config.MAX_BUFF_USAGE, load=config.LOAD):
        """
        Calculates the proportion of the buffer that is allowed to be used up
        """
        instructions_done = instructions_planned - instructions_left
        process_completion = instructions_done / instructions_planned
        if process_completion < 0.05:
            process_completion = 0.05
        available_buffer = buffer * load #* self.CONSUMEABLE_BUFFER
        usable_buffer = available_buffer * process_completion

        assert usable_buffer < available_buffer
        assert usable_buffer >= 0  # t2 with 0% completion should just be one of other thresholds

        return int(usable_buffer)
