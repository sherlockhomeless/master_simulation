from typing import List, Dict

import helper
from task import Task
from process import Process
from threshold_interface import thresholder
from job_scheduler import JobScheduler
from plan import Plan
from helper import PlanFinishedException
import config


class ProcessRunner:
    def __init__(self, plan: Plan):
        """
        The "runtime" environment for simulating a running node.

        : param plan: The plan PR needs to run
        : param tick_log: path to where the log per tick is written too
        : param thresh_log: path to where the threshold will be logged too
        : param thresh_log_pure: threshold logging for the threshold independant of it's plan/real length
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
        self.job_sched = JobScheduler(self.task_list)
        self.finished_tasks: List[Task] = []

        self.thresholds: Dict = {}

        self.tick_counter = 0
        self.stress = 0
        self.lateness_node: int = 0
        self.lateness_neutralizer: int = 0
        self.length_plan = sum([sum(tasks_in_p.tasks) for tasks_in_p in self.processes])

        if config.LOG is True:
            self.log_unified = open(config.unified_log_path, 'w')

            self.t1_pure = 0
            self.t2_pure = 0
            self.tm2_pure = 0

    def run(self):
        try:
            while not self.has_finished():
                self.run_tick()
                if config.LOG and self.cur_task.task_id != -1:
                    self.write_unified_log()
            config.logger.debug(f'[{self.tick_counter}]: current task {self.cur_task}')
        except PlanFinishedException:
            config.logger.info(f'[{self.tick_counter}][FINISHED]: Ran {len(self.finished_tasks)} tasks, '
                           f'sent {len(self.job_sched.received_signals)} PFSs')

    def run_tick(self):
        """
        Simulates the equivalent of an timer tick. Updates the Threshold and executes the appropriate actions
        if a threshold is transgressed
        """
        def hold_at_tick(tick_count: int):
            """
            Helper function to stop execution at given tick-count
            """
            if self.tick_counter == tick_count:
                print('stop here')

        def is_t2_triggered(cur_process, cur_task) -> bool:
            t2_task_triggered = thresholder.check_t2_task(cur_task.instructions.plan,
                                                          self.thresholds['t2_task'])
            t2_process_triggered = thresholder.check_t2_process(cur_process.lateness, self.thresholds['t2_process'])
            t2_node_triggered = thresholder.check_t2_node(self.lateness_node, self.thresholds['t2_node'])
            t2_preemptions_triggered = thresholder.check_t2_preemptions(cur_task)
            trigger = t2_task_triggered or t2_process_triggered or t2_node_triggered or t2_preemptions_triggered
            if trigger:
                config.logger.warn(f'[{self.tick_counter}] t2_task: {t2_task_triggered} ({self.cur_task.get_lateness_task()})/{self.thresholds["t2_task"]},'
                      f' t2_process: {t2_process_triggered} ({self.cur_process.lateness}/{self.thresholds["t2_process"]}), '
                      f' t2_node: {t2_node_triggered} ({self.lateness_node}/{self.thresholds["t2_node"]}), '
                      f' t2_preemptions: {t2_preemptions_triggered} ({self.cur_task.was_preempted}/{config.T2_MAX_PREEMPTIONS})')
            return trigger
        hold_at_tick(12030237415)
        self.update_thresholds()

        # --- convenience variables ---
        cur_task = self.cur_task
        cur_process = self.cur_process
        cur_task_id = cur_task.task_id

        # runs the full set of instructions on the current task
        cur_task.run(self.ipt)
        self.update_process_and_node_lateness()
        # --- Task has finished ---
        if cur_task.has_task_finished():
            try:
                self.handle_task_finish(cur_process, cur_task, cur_task_id)
            except helper.PlanFinishedException:
                assert len(self.task_list) == 0
                return

        # --- Task has NOT finished ---
        elif cur_task.is_task_late():
            instructions_run_slot = cur_task.get_instructions_cur_slot()

            if instructions_run_slot >= self.thresholds['t1']:
                old_task = self.cur_task
                self.preempt_current_task()
                config.logger.info(f'[{self.tick_counter}] {old_task} was preempted for {self.cur_task}')

        if is_t2_triggered(cur_process, cur_task):
            self.signal_t2()
            self.receive_updated_plan()

        self.tick_counter += 1
        self.stress -= 1 if self.stress > 0 else 0

    def handle_task_finish(self, cur_process, cur_task, cur_task_id):
        instructions_left_in_tick = cur_task.get_overdone_instructions()
        if cur_task.has_task_finished_early():
            tm2_task_triggered = thresholder.check_tm2_task(cur_task.instructions.instructions_retired_task,
                                                            self.thresholds['tm2_task'])
            tm2_node_triggered = thresholder.check_tm2_node(self.lateness_node, self.thresholds['tm2_node'], self.stress)
            if tm2_task_triggered or tm2_node_triggered:
                self.task_list = self.job_sched.signal_t_m2(self.tick_counter, cur_task, self.task_list)
                config.logger.warn(f'[{self.tick_counter}] '
                                   f'tm2_task: {tm2_task_triggered} ({self.cur_task.get_lateness_task()}/{self.thresholds["t2_task"]},'
                                   f'tm2_node: {tm2_node_triggered} ({self.cur_process.lateness}/{self.thresholds["t2_process"]})')
                self.receive_updated_plan()
        self.update_process_and_node_lateness()
        self.pick_next_task()
        config.logger.info(f'[{self.tick_counter}] finished Task {cur_task_id}; started Task {self.cur_task.task_id}')
        self.cur_task.run(instructions_left_in_tick)

    def find_slot_for_preemption(self, start_search_index, assign_free_slots=False):
        """
        :param start_search_index: start searching from here
        :param assign_free_slots: Enable/Disable looking for free slots
        :return: Index of the task slot found in the plan
        """
        for i in range(start_search_index, len(self.task_list)):
            if self.task_list[i].process_id == -1 and assign_free_slots:
                return i
            elif self.task_list[i].process_id == self.cur_task.process_id:
                return i
        raise PlanFinishedException

    def move_preempted_task(self, preempted_task: Task, insertion_index: int):
        """
        * Moves the preempted task (stack) into slot of insertion task
        * Updates slots for all moved tasks
        """
        insertion_task = self.task_list[insertion_index]
        assert insertion_task.process_id == preempted_task.process_id

        tasks_to_move = list(filter(lambda t: t.process_id == preempted_task.process_id,
                                    self.task_list[:insertion_index]))
        for task in tasks_to_move:
            self.task_list.insert(insertion_index, task)
            self.task_list.remove(task)
            task.preempt(insertion_task)

    def preempt_current_task(self):
        """
        * preempts the currently running task
        * inserts the remaining part where the next task of the process would start
        * prepares starting the next process
        """

        # --- convenience variables ---
        preempted_task = self.cur_task
        cur_task_id = self.cur_task.task_id
        next_task_index = self.search_task_following(cur_task_id)
        len_plan_start = len(self.task_list)

        config.logger.info(f'[{self.tick_counter}]:{preempted_task} was preempted')

        # looking for a slot in the plan where preempted_task can get inserted too
        insertion_index = self.find_slot_for_preemption(next_task_index)
        insertion_task = self.task_list[insertion_index]
        config.logger.debug(f'[{self.tick_counter}] task {preempted_task} is inserted before {insertion_task}')

        # --- inserting preempted-task before slot ---
        self.move_preempted_task(preempted_task, insertion_index)

        # --- move plan forward and set timer ---
        self.cur_task = self.task_list[0]
        self.tick_counter += config.COST_CONTEXT_SWITCH

        # mark the task as already preempted
        preempted_task.was_preempted += 1
        config.logger.info(f'[{self.tick_counter}][preemption] task {preempted_task.task_id} was preempted {preempted_task.was_preempted} times')

        if self.cur_task.task_id == -1:
            self.pick_next_task()
            return  # the assert below does not need to hold in this case
        assert len(self.task_list) == len_plan_start

    def pick_next_task(self):
        import helper
        """
        : param instructions_left: int, number of instructions left in current tick
        Picks the next task
        ! shortens the plan
        """
        def assign_task_to_free_slot(inserted_task: Task, task_list: List[Task]) -> List[Task]:
            free_slot: Task = task_list[0]
            assert free_slot == -1
            assert inserted_task.was_preempted > 0

            # remove from original slot & insert to unallocated slot
            task_list.remove(inserted_task)
            task_list[0] = inserted_task

            inserted_task.length_plan += free_slot.length_plan

        def idle():
            self.tick_counter += self.task_list[0].instructions.plan
            self.task_list = self.task_list[1:]
            try:
                self.cur_task = self.task_list[0]
            except IndexError:
                raise PlanFinishedException
            config.logger.info(f'[{self.tick_counter}] idling')

        def handle_unallocated_slot():
            """
            If the PR encounters an slot with pid -1 it has to execute this handler method
            """
            # get all upcoming tasks
            first_tasks: List[Task] = []
            for process in self.processes:
                first_task: Task = helper.get_next_task_for_process(self.task_list, process)
                if first_task is not None:
                    continue
            preempted_task_list = list(filter(lambda t: t.was_preempted != 0, first_tasks))
            if len(preempted_task_list) == 0:
                idle()
            else:
                pids_with_preemption = list(map(lambda t: t.process_id, preempted_task_list))
                ps_with_preemption = list(filter(lambda pid: helper.get_process_with_pid(pid, self.processes), pids_with_preemption))
                ps_with_preemption.sort(key=lambda p: p.lateness, reverse=True)
                latest_process = ps_with_preemption[0]
                task_to_assign = list(filter(lambda t: t.process_id == latest_process.process_id, preempted_task_list))[0]
                assign_task_to_free_slot(task_to_assign, self.task_list)

        if self.cur_task.process_id == -1:
            handle_unallocated_slot()
            return

        self.finish_cur_task()

        self.tick_counter += config.COST_CONTEXT_SWITCH
        if self.cur_task.process_id == -1:
            handle_unallocated_slot()

    def update_thresholds(self):
        """
        It calculates all the thresholds relevant for the upcoming timer tick.
        :return:
        """

        cur_task = self.cur_task

        cur_process_id = cur_task.process_id
        cur_process = self.processes[cur_process_id]

        instructions_planned_task = self.cur_task.instructions.plan
        # --- calculate t1 ---
        t1 = thresholder.compute_t1(cur_task)
        self.thresholds['t1'] = t1
        self.thresholds['t1_pure'] = t1 - instructions_planned_task

        # --- calculate t2 ---
        t2_task = thresholder.compute_t2_task(instructions_planned_task, self.stress * config.T2_STRESS_GAIN)
        self.thresholds['t2_task'] = t2_task
        self.thresholds['t2_task_pure'] = t2_task - instructions_planned_task
        t2_process = thresholder.compute_t2_process(cur_process, self.stress, self.finished_tasks + [cur_task])

        self.thresholds['t2_process'] = t2_process
        planned_length_all_finished_tasks = sum(list([t.instructions.plan for t in self.finished_tasks]))
        length_first_10 = sum(self.task_list[:10])
        ins_planned = length_first_10 if planned_length_all_finished_tasks < length_first_10 else planned_length_all_finished_tasks
        t2_node = thresholder.compute_t2_node(ins_planned, self.stress)
        self.thresholds['t2_node'] = t2_node
        t2_preemptions = thresholder.compute_t2_preemptions(cur_task)
        self.thresholds['t2_preemptions'] = t2_preemptions

        # --- calculate tm2 ---
        tm2_task = thresholder.compute_tm2_task(instructions_planned_task)
        self.thresholds['tm2_task'] = tm2_task
        self.thresholds['tm2_task_pure'] = tm2_task - instructions_planned_task
        tm2_node = thresholder.compute_tm2_node(self.thresholds['t2_node'])
        self.thresholds['tm2_node'] = tm2_node

        assert self.thresholds['t1'] < self.thresholds['t2_task'] or self.cur_task.was_preempted

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

    def update_process_and_node_lateness(self):
        """
        Updates the lateness of the current process and of the node

        :return:
        """
        self.cur_process.update_lateness()
        lateness_node = sum([p.lateness for p in self.processes])
        self.lateness_node = lateness_node + self.lateness_neutralizer

    def transgresses_t1(self) -> bool:
        """
        cur_task_ins ---- t1 ---- 0 ---- plan_ins
        determines if cur_task_ins is located such that t1 is transgressed
        """
        t1 = -1 * self.thresholds[self.cur_task.process_id].t1
        cur_lateness = self.cur_task.instructions.plan
        return True if t1 > cur_lateness else False

    def signal_t2(self):
        """
        Should signal to the VRM that there is an significant failure with the prediction of the prediction model.
        In this simulation this step is kept very simple
        """
        self.stress = config.T2_STRESS_RESET
        self.job_sched.signal_t2(self.tick_counter, self.cur_task, self.task_list)

    def finish_cur_task(self):
        assert self.cur_task.has_task_finished()

        self.finished_tasks.append(self.cur_task)
        self.task_list = self.task_list[1:]
        if len(self.task_list) == 0:
            raise PlanFinishedException
        else:
            self.cur_task = self.task_list[0]
            self.cur_process = self.processes[self.cur_task.process_id]

    def receive_updated_plan(self):
        """
        One assumption made is that the job schedulers updates plans in such a way
        that the signaled prediction failure is taken care of
        :return:
        """
        self.lateness_neutralizer = -self.lateness_node
        self.cur_process.lateness_neutralizer = -self.cur_process.lateness

    def write_unified_log(self) -> None:
        """
        Format: Tick;t1_sum;t1_pure;t2_task_sum;t2_task_pure;t2_process;t2_node;tm2_task_sum;tm2_task_pure;tm2_node;
        task_id;task_length_plan_unchanged;task_lenght_plan;task_length_real;lateness;preemptions;
        process_id;process_lateness;node_lateness
        :return:
        """
        tick = self.tick_counter

        t1_sum = self.thresholds['t1']
        t1_pure = self.thresholds['t1_pure']
        t2_task_sum = self.thresholds['t2_task']
        t2_task_pure = self.thresholds['t2_task_pure']
        tm2_task_sum = self.thresholds['tm2_task']
        tm2_task_pure = self.thresholds['tm2_task_pure']

        t2_process_capacity = self.thresholds['t2_process'][0]
        t2_process_plan = self.thresholds['t2_process'][1]

        t2_node = self.thresholds['t2_node']
        tm2_node = self.thresholds['tm2_node']

        cur_task_id = self.cur_task.task_id
        cur_task_len_unchanged = self.cur_task.instructions.plan
        cur_task_len_plan = int(self.cur_task.instructions.instructions_retired_task)
        cur_task_len_real = self.cur_task.length_real
        lateness_task = self.cur_task.get_lateness_task()
        preemptions = self.cur_task.was_preempted
        cur_process_id = self.cur_process.process_id
        lateness_process = self.cur_process.lateness
        lateness = self.lateness_node

        line_thresholds = f'tick:{tick};t1_sum:{t1_sum};t1_pure:{t1_pure};t2_task_sum:{t2_task_sum};' \
                          f't2_task_pure:{t2_task_pure};t2_process_capacity:{t2_process_capacity}' \
                          f';t2_process_plan:{t2_process_plan};t2_node:{t2_node};' \
                          f'tm2_task_sum:{tm2_task_sum};tm2_task_pure:{tm2_task_pure};tm2_node:{tm2_node};'
        line_task = f'cur_task_id:{cur_task_id};cur_task_len_unchanged:{cur_task_len_unchanged};' \
                    f'cur_task_len_plan:{cur_task_len_plan};cur_task_len_real:{cur_task_len_real};' \
                    f'lateness_task:{lateness_task};preemptions:{preemptions};'
        line_rest = f'process_id:{cur_process_id};lateness_process:{lateness_process};lateness_node:{lateness}'
        log_string = line_thresholds + line_task + line_rest + '\n'
        self.log_unified.write(log_string)

    @staticmethod
    def get_process_runner(new_plan):
        return ProcessRunner(new_plan)

    def __repr__(self) -> str:
        return f"{'lateness_node': {self.lateness_node}}"
