from typing import List

import config
from task import Task
from process import Process
from thresholder import Threshold
from vrm import VRM
from plan import Plan
import config


class ProcessRunner:
    def __init__(self, plan, tick_log=config.tick_log_path, thresh_log=config.thresh_log_path, thresh_log_pure=config.thresh_log_pure, ipt=1):
        """
        The "runtime" environment for simulating a running node.

        : param plan: The plan PR needs to run
        : param tick_log: path to where the log per tick is written too
        : param thresh_log: path to where the threshold will be logged too
        : param thresh_log_pure: threshold logging for the threshold independant of it's plan/real length
        : param ipt: instructions to run per tick
        : param log: enable logging to file?
        : param breakpoint: ticks after which the PR should stop for debugging/testing reasons
        """
        assert type(plan) is Plan

        self.ipt: int = config.INS_PER_TICK
        self.task_list: List[Task] = plan.task_list
        self.processes: List[Process] = plan.processes
        self.number_processes: int = len(self.processes)
        self.number_tasks = plan.number_all_tasks
        self.cur_task = self.task_list[0]
        self.cur_process = self.processes[self.cur_task.process_id]
        self.cur_process_id = self.cur_process.process_id
        self.vrm = VRM(self.task_list)

        self.t1 = None
        self.t2 = None
        self.t_m2 = None

        self.finished_tasks = 0
        self.time = 0

        if config.LOG is True:
            self.tick_log = open(tick_log, 'w')
            self.log_thresh = open(thresh_log, 'w')
            self.log_thresh_pure = open(thresh_log_pure, 'w')
            self.t1_pure = 0
            self.t2_pure = 0
            self.tm2_pure = 0
        else:
            self.thresh_log = open('/dev/null', 'w')

    def run_tick(self):
        '''
        Simulates the equivalent of an timer tick. Updates the Threshold and executes the appropriate actions if a threshold is transgressed
        '''

        # --- update on task & process level ---
        assert self.cur_task.length_real > 0

        # TODO: Assert t1 is calculated correctly for preempted tasks
        self.update_thresholds()

        # --- convenience variables ---
        cur_task = self.cur_task
        cur_process = self.cur_process
        cur_process_id = cur_process.process_id
        cur_task_id = cur_task.task_id

        # runs the full set of instructions on the current task
        cur_task.run(self.ipt)

        # --- Task has finished ---
        if cur_task.has_task_finished():
            instructions_left_in_tick = cur_task.get_overdone_instructions()

            if cur_task.has_task_finished_early():
                earliness = cur_task.get_early_instructions(instructions_left_in_tick)
                if earliness < self.t_m2:
                    self.vrm.signal_t_m2(self.time, cur_task)

            self.pick_next_task()
            cur_task.run(instructions_left_in_tick)

        # --- Task has NOT finished ---
        elif cur_task.is_task_late():
            instructions_run_task = cur_task.instruction_counter.instructions_task
            instructions_run_slot = cur_task.get_instructions_cur_slot()
            cur_t1, cur_t2 = self.t1, self.t2
            if instructions_run_slot >= cur_t1:
                # preempt if not already preempted
                if not cur_task.was_preempted:
                    self.preempt_current_process()
                if instructions_run_task >= cur_t2:
                    self.vrm.signal_t2(self.time, cur_task)
        self.time += self.ipt

        if config.LOG:
            self.write_thresh_log()
            self.write_tick_log()
            if config.LOG_TERM:
                print(f'time: {self.time}, task: {self.cur_task}')

    def transgresses_t1(self) -> bool:
        """
        cur_task_ins ---- t1 ---- 0 ---- plan_ins
        determines if cur_task_ins is located such that t1 is transgressed
        """
        t1 = -1 * self.thresholds[self.cur_task.process_id].t1
        cur_lateness = self.cur_task.length_plan
        return True if t1 > cur_lateness else False

    def preempt_current_process(self):
        """
        preempts the currently running task, inserts the remaining part where the next task of the process would start and starts the next process
        [CHECK] where to change things after preemption?
        [TODO] Let process only run amount of time that other task has available
        """
        def find_slot_for_preemption(start_search_index, assign_free_slots = False):
            """
            :param start_search_index: start searching from here
            :param assign_free_slots: Enable/Disable looking for free slots
            :return: Index of the task slot found in the plan
            """
            for i in range(start_search_index, len(self.task_list)):
                if self.task_list[i].process_id == -1 and assign_free_slots:
                    return i
                elif self.task_list[i].process_id == cur_process_id:
                    return i
            raise IndexError

        def move_preempted_task(preempted_task: Task, insertion_slot: int):
            """
            Moves the preemted Task and tasks it shared a slot with into another plan slot indicated by next_slot
            :param preempted_task: Task to move into other slot
            :param insertion_slot: Index of Insertion Task in Plan
            :return:
            """
            insertion_task = self.task_list[insertion_slot]
            assert insertion_task.process_id == preempted_task.process_id

            tasks_to_move = (preempted_task, *preempted_task.shares_slot_with)
            for t in tasks_to_move:
                self.task_list.insert(insertion_slot, t)
            preempted_task.preempt(insertion_task)

        # --- convenience variables ---
        preempted_task = self.cur_task
        preempted_task.was_preempted += 1
        cur_task_id = self.cur_task.task_id
        cur_process_id = self.cur_task.process_id
        next_task_index = self.search_task_following(cur_task_id)
        found_slot = False
        # looking for a slot in the plan where preempted_task can get inserted too
        while found_slot is False:
            insertion_index = find_slot_for_preemption(next_task_index)
            insertion_task = self.task_list[insertion_index]

            # preempted_task is of same process as found task
            if insertion_task.process_id == cur_process_id:
                config.logger.debug(f'task {preempted_task} may inserted before {insertion_task}')
                found_slot = True

            # found task is unallocated
            elif config.INSERT_PREEMPTED_IN_FREE and insertion_task.process_id == -1:
                preempted_task.shares_slot(insertion_index)
                config.logger.debug(f'task {preempted_task} may be inserted before free slot')

            # found nothing fitting at current slot
            else:
                continue

        # --- inserting preempted-task before slot ---
        move_preempted_task(preempted_task, insertion_index)

        # --- move plan forward and set timer ---
        self.cur_task.was_preempted = True
        self.task_list = self.task_list[1:]
        self.cur_task = self.task_list[0]
        self.time += config.COST_CONTEXT_SWITCH

        # mark the task as already preempted
        preempted_task.was_preempted += 1
        

    def signal_prediction_failure(self):
        """
        Should signal to the VRM that there is an significant failure with the prediction of the prediction model.
        In this simulation this step is kept very simple
        """
        pass

    def pick_next_task(self):
        """
        : param instructions_left: int, number of instructions left in current tick
        Picks the next task
        ! shortens the plan
        """
        self.task_list = self.task_list[1:]
        if len(self.task_list) == 0:
            return
        self.time += config.COST_CONTEXT_SWITCH
        self.cur_task = self.task_list[0]
        self.cur_process = self.processes[self.cur_task.process_id]

    def run(self):
        while self.has_finished is False:
            self.run_tick()

    def update_thresholds(self):
        """
        It calculates all the thresholds relevant for the upcoming timer tick.
        :return:
        """
        cur_task = self.cur_task

        cur_process_id = cur_task.process_id
        cur_process = self.processes[cur_process_id]
        cur_process_buff = cur_process.buffer

        # check if task was preempted and is in other slot
        if cur_task.was_preempted != 0:
            tasks_of_current_slot = cur_task.shares_slot_with[-1]
            instructions_planned = tasks_of_current_slot.length_plan_unchanged
        else:
            instructions_planned = cur_task.length_plan_unchanged

        # --- calculate t1 ---

        self.t1 = Threshold.calc_t1(instructions_planned)

        self.t2 = Threshold.calc_t2(
            cur_process_buff,
            instructions_planned,
            cur_process.instructions_executed,
            cur_process.process_length,
            self.t1,
            cur_task.was_preempted
        )

        self.t_m2 =Threshold.calc_t_minus(self.t2)

        if config.LOG:
            self.t1_pure = self.t1 - cur_task.length_plan_unchanged
            self.t2_pure = self.t2 - cur_task.length_plan_unchanged
            self.tm2_pure = self.t_m2
            self.write_thresh_log()


    def has_finished(self) -> bool:
        return False if len(self.task_list) > 0 else True

    def search_task_following(self, cur_id) -> int:
        """
        Returns the index of the task that is following the task with the given id according to the plan
        """
        for i, t in enumerate(self.task_list):
            if t.task_id == cur_id:
                return i+1
        return len(self.task_list)

    def write_plan_to_file(self, path):
        meta = f'{len(self.processes)};'
        # meta = f'{len(self.processes)},{len(self.plan)};;'
        for i, p in enumerate(self.processes):
            meta += f'{i},{i},{p.buffer},{p.deadline};'

        tasks_s = ''
        for task in self.task_list:
            tasks_s += f'{task.process_id},{task.process_id},{task.task_id},{task.length_plan},{task.length_real};'

        plan_s = meta + ";;" + tasks_s

        with open(path, 'w') as f:
            f.write(plan_s)
            # now again in human readable ;)
            f.write('\n\n#########\n\n')
            for task in self.task_list:
                f.write(
                    f'{task.process_id} {task.process_id} {task.task_id} {task.length_plan} {task.length_real}\n')

    def write_thresh_log(self):
        """
        Writes the current state of the thresholds to a file
        :return:
        """
        # format: cur_jobid cur_process_id cur_task_id cur_t1 cur_t2 cur_-t2
        assert config.LOG is True

        if self.cur_task.task_id != -1:
            self.log_thresh.write(
                f'{self.cur_task.task_id} {self.t1} {self.t2} {self.t_m2}\n')
            self.log_thresh_pure.write(
                f'{self.cur_task.task_id} {self.t1_pure} {self.t2_pure} {self.tm2_pure}\n')

        else:
            self.log_thresh.write('-1 0 0 0\n')  # empty space

    def write_tick_log(self):
        """
        Writes Task-Information and the current time to File
        FORMAT :[Task] Time
        :return: None
        """
        self.tick_log.write(
            f'{self.time} {str(self.cur_task)}\n')

    def __del__(self):
        if config.LOG is False:
            return
        try:
            self.tick_log.close()
            self.log_thresh.close()
            self.log_thresh_pure.close()
            self.thresh_log.close()
        except AttributeError:
            pass




    @staticmethod
    def get_process_runner(new_plan):
        return ProcessRunner(new_plan)
