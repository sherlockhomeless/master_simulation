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
    def calc_t2(instructions_planned_task: int, t1: int,
                usable_buffer: int, stress: int,
                instructions_planned_total: int) -> {}:
        """
        :param t1: the value for t1 calculated before
        :param instructions_planned_task: instructions planned for the currently running task
        :param usable_buffer: usable buffer for currently running process
        :param stress: stress on the node
        :param instructions_planned_total: instructions planned of
        :return: dictionary with all the t2 components

        todo: enable or disable option for components
        """
        thresholds = {}
        # --- t2_task ---
        t2_task = instructions_planned_task * config.CAP_LATENESS
        t2_task = t1 + config.T2_SPACER if t2_task < t1 else t2_task
        thresholds['t2_task'] = t2_task

        # --- t2_process ---
        t2_process = usable_buffer + (stress * config.INS_PER_TICK) - config.RESCHEDULE_TIME
        thresholds['t2_process'] = t2_process
        # --- t2_node ---
        if config.T2_NODE_ENABLED:
            t2_node = (instructions_planned_total * config.MAX_LATENESS_NODE) - instructions_planned_total
            thresholds['t2_node'] = t2_node
        else:
            thresholds['t2_node'] = None

        # --- t2_preemptions ---
        t2_preemptions = config.T2_MAX_PREEMPTIONS
        thresholds['t2_preemptions'] = t2_preemptions

        return thresholds

    @staticmethod
    def check_t2(t2: {}, instructions_planned_task: int, run_instructions_task: int,
                 lateness_process: int, lateness_node: int, preemptions: int) -> bool:
        if run_instructions_task >= t2['t2_task'] + instructions_planned_task:
            return True
        elif lateness_process >= t2['t2_process']:
            return True
        elif config.T2_NODE_ENABLED and lateness_node >= t2['t2_node']:
            return True
        elif preemptions >= t2['t2_preemptions']:
            return True
        else:
            return False

    @staticmethod
    def calc_t2_minus(t2_task: int, t2_node: int) -> {}:
        """
        Calculates the threshold values for t-2
        :param t2_task:
        :param t2_node:
        :return:
        """
        tm2_task = t2_task * -1
        tm2_node = t2_node * -1 if t2_node is not None else None

        return {'tm2_task': tm2_task, 'tm2_node': tm2_node}

    @staticmethod
    def check_tm2(tm2: {}, instructions_run_task: int, lateness_node: int) -> bool:
        if instructions_run_task <= tm2['tm2_task']:
            return True
        elif lateness_node <= tm2['tm2_node']:
            return True
        else:
            return False



    @staticmethod
    def calc_usable_buffer(instructions_planned_process, instructions_left, buffer_process: int, free_time=1.0):
        """
        Calculates the proportion of the buffer that is allowed to be used up
        :param instructions_planned_process: the sum of all instructions planned for the process
        :param instructions_left: the sum of all instructions that still have to be executed according to the plan
        :param buffer: the buffer given to the process
        :param load :
        :return:
        """
        instructions_done = instructions_planned_process - instructions_left
        process_completion = instructions_done / instructions_planned_process
        cleared_buffer = buffer_process * free_time
        available_buffer = cleared_buffer * config.ASSIGNABLE_BUFFER

        if process_completion < 0.05:
            process_completion = 0.05

        usable_buffer = available_buffer * process_completion

        assert usable_buffer < available_buffer
        assert usable_buffer >= 0  # t2 with 0% completion should just be one of other thresholds

        return int(usable_buffer)
