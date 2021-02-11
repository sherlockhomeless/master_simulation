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
    no_preemption = config.NO_PREEMPTION
    # --- PARAS t2 ---
    # how much of the buffer is available for usage
    consumable_buffer = config.CONSUMABLE_BUFFER
    # how much is a task allowed to deviate from it's plan, eg. 120% => 1.2
    cap_lateness = config.CAP_LATENESS
    # factor that determines how much bigger t2 has to be then t1
    spacer_constant = config.SPACER_CONSTANT

    @staticmethod
    def calc_t1(instructions_planned) -> int:
        '''
        Calculates the t1 at which the currently running task is preempted and replaced by the next task in the plan.
        t1 is the minimum off two values, one of which represents an absolute boundary, the other a relative boundary:

            * max_global_deviation => is a global boundary that ensures that independant of the task details, a certain amount of ticks is not transgressed
            * max_local_deviation => is a local, relative boundary relating to the details of the task TODO: AND PROCESS
        '''
        relative_t1 = max(instructions_planned * Threshold.sigma_t1, Threshold.no_preemption)
        t1 = int(min(relative_t1, Threshold.preempt_limit))

        return t1

    @staticmethod
    def calc_t2(usable_buffer, length_plan, stress=0, load) -> int:
        """
        Triggers PredictionFailure to VRM. Conditions:
        1. Individual Task was extremly off => in current implementation this condition holds if one task takes the amount of two slots of the assigned time
        2. Whole Process is off by significant amount proportional to state of progress

        [TODO] static threshhold depending on stress level
        """

        t2_relative_buffer = self.t1 + usable_buffer + stress * self.ipt - self.reschedule_time
        t2_cap_lateness = self.CAP_LATENESS * length_plan
        t2_process_state = t2_cap_lateness  # IMPLEMENT
        t2 = min(t2_relative_buffer, t2_cap_lateness, t2_process_state)
        t2 = int(t2)
        assert self.t1 < t2
        return t2 if t2 > self.t1 else self.t1 * self.SPACER_CONSTANT

    @staticmethod
    def calc_t_minus(instructions_planned):
        raise NotImplementedError
        return int(-1 * self.t2 * 2)

    @staticmethod
    def calc_usable_buffer(instructions_planned, instructions_left):
        """
        Calculates the proportion of the buffer that is allowed to be used up
        """
        instructions_done = instructions_planned - instructions_left
        process_completion = instructions_done / instructions_planned
        if process_completion < 0.05:
            process_completion = 0.05
        available_buffer = self.buffer * self.load * self.CONSUMEABLE_BUFFER
        usable_buffer = available_buffer * process_completion

        assert usable_buffer < available_buffer
        assert usable_buffer >= 0  # t2 with 0% completion should just be one of other thresholds

        return int(usable_buffer)
