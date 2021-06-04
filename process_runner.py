from typing import List, Dict

from task import Task
from process import Process
from thresholder import thresholder
from vrm import VRM
from plan import Plan
import config


class ProcessRunner:
    def __init__(self, plan: Plan, tick_log=config.tick_log_path, thresh_log=config.thresh_log_path, thresh_log_pure=config.thresh_log_pure):
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
        self.vrm = VRM(self.task_list)
        self.finished_tasks: List[Task] = []

        self.thresholds: Dict = {}

        self.tick_counter = 0
        self.stress = 0
        self.lateness_node: int = 0
        self.length_plan = sum([sum(tasks_in_p.tasks) for tasks_in_p in self.processes])

        if config.LOG is True:
            self.log_unified = open(config.unified_log_path, 'w')
            self.tick_log = open(tick_log, 'w')
            self.log_thresh = open(thresh_log, 'w')
            self.log_thresh.write('{tick} {task_id} {t1} {t2} {t_m2}\n')

            self.log_thresh_pure = open(thresh_log_pure, 'w')
            self.log_thresh_pure.write('{tick} {task_id} {t1} {t2} {t_m2}\n')
            self.t1_pure = 0
            self.t2_pure = 0
            self.tm2_pure = 0

    def run_tick(self):
        """
        Simulates the equivalent of an timer tick. Updates the Threshold and executes the appropriate actions if a threshold is transgressed
        """

        def is_t2_triggered(cur_process, cur_task) -> bool:
            t2_task_triggered = thresholder.check_t2_task(cur_task.instruction_counter.instructions_task,
                                                          self.thresholds['t2_task'])
            t2_process_triggered = thresholder.check_t2_process(cur_process.lateness, self.thresholds['t2_process'])
            t2_node_triggered = thresholder.check_t2_node(self.lateness_node, self.thresholds['t2_node'])
            t2_preemptions_triggered = thresholder.check_t2_preemptions(cur_task)
            return t2_task_triggered or t2_process_triggered or t2_node_triggered or t2_preemptions_triggered

        # --- update on task & process level ---
        assert self.cur_task.length_real > 0

        # TODO: Assert t1 is calculated correctly for preempted tasks
        self.update_thresholds()

        # --- convenience variables ---
        cur_task = self.cur_task
        cur_process = self.cur_process
        cur_task_id = cur_task.task_id

        # runs the full set of instructions on the current task
        cur_task.run(self.ipt)

        # --- Task has finished ---
        if cur_task.has_task_finished():
            self.handle_task_finish(cur_process, cur_task, cur_task_id)

        # --- Task has NOT finished ---
        elif cur_task.is_task_late():
            instructions_run_task = cur_task.instruction_counter.instructions_task
            instructions_run_slot = cur_task.get_instructions_cur_slot()

            if instructions_run_slot >= self.thresholds['t1']:
                self.preempt_current_process()

            if is_t2_triggered(cur_process, cur_task):
                self.signal_t2()

        self.tick_counter += 1

        if config.LOG and self.cur_task.task_id != -1:
            self.write_unified_log()
            #self.write_thresh_log()
            #self.write_tick_log()
            if config.LOG_TERM:
                print(f'time: {self.tick_counter}, task: {self.cur_task}')

    def handle_task_finish(self, cur_process, cur_task, cur_task_id):
        print(f'task {cur_task_id} has finished')
        instructions_left_in_tick = cur_task.get_overdone_instructions()
        if len(cur_process.tasks) == 0:
            self.mark_process_finished()
        if cur_task.has_task_finished_early():
            tm2_task_triggered = thresholder.check_tm2_task(cur_task.instruction_counter.instructions_task,
                                                            self.thresholds['tm2_task'])
            tm2_node_triggered = thresholder.check_tm2_node(self.lateness_node, self.thresholds['tm2_node'])
            if tm2_task_triggered or tm2_node_triggered:
                self.vrm.signal_t_m2(self.tick_counter, cur_task, self.task_list)
        self.update_process_node_lateness()
        self.pick_next_task()
        cur_task.run(instructions_left_in_tick)

    def update_process_node_lateness(self):
        lateness_node = sum([p.lateness for p in self.processes])
        lateness_process = sum([t.get_lateness_task() for t in filter
        (lambda task: task.process_id == self.cur_process.process_id, self.finished_tasks)])
        self.lateness_node = lateness_node
        self.cur_process.lateness = lateness_process

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
            Moves the preemted Tasks and tasks it shared a slot with into another plan slot indicated by next_slot
            :param preempted_task: Task to move into other slot
            :param insertion_slot: Index of Insertion Task in Plan
            :return:
            """
            insertion_task = self.task_list[insertion_slot]
            assert insertion_task.process_id == preempted_task.process_id

            tasks_to_move = (preempted_task, *preempted_task.shares_slot_with)
            for t in tasks_to_move:
                self.task_list.remove(t)
                self.task_list.insert(insertion_slot-1, t)
            preempted_task.preempt(insertion_task)
        # --- convenience variables ---
        preempted_task = self.cur_task
        preempted_task.was_preempted += 1
        cur_task_id = self.cur_task.task_id
        cur_process_id = self.cur_task.process_id
        next_task_index = self.search_task_following(cur_task_id)
        len_plan_start = len(self.task_list)
        found_slot = False

        if config.LOG:
            config.logger.info(f'@{self.tick_counter}:{preempted_task} was preempted')

        # looking for a slot in the plan where preempted_task can get inserted too
        while found_slot is False:
            try:
                insertion_index = find_slot_for_preemption(next_task_index)
                insertion_task = self.task_list[insertion_index]
            except IndexError:
                raise NotImplementedError

            # preempted_task is of same process as found task
            if insertion_task.process_id == cur_process_id and insertion_task not in preempted_task.shares_slot_with:
                config.logger.debug(f'task {preempted_task} may inserted before {insertion_task}')
                found_slot = True

            # found task is unallocated
            elif config.INSERT_PREEMPTED_IN_FREE and insertion_task.process_id == -1:
                preempted_task.shares_slot(insertion_index)
                config.logger.debug(f'task {preempted_task} may be inserted before free slot')

            # found nothing fitting at current slot
            else:
                next_task_index += 1
                continue

        # --- inserting preempted-task before slot ---
        move_preempted_task(preempted_task, insertion_index)

        # --- move plan forward and set timer ---
        self.cur_task.was_preempted = True
        self.cur_task = self.task_list[0]
        self.tick_counter += config.COST_CONTEXT_SWITCH

        # mark the task as already preempted
        preempted_task.was_preempted += 1
        assert len(self.task_list) == len_plan_start

    def signal_t2(self):
        """
        Should signal to the VRM that there is an significant failure with the prediction of the prediction model.
        In this simulation this step is kept very simple
        """
        self.stress += config.STRESS_PER_SIGNAL
        self.vrm.signal_t2(self.tick_counter, self.cur_task, self.task_list)

    def pick_next_task(self):
        """
        : param instructions_left: int, number of instructions left in current tick
        Picks the next task
        ! shortens the plan
        """
        self.finished_tasks.append(self.cur_task)
        self.task_list = self.task_list[1:]
        if len(self.task_list) == 0:
            return
        self.tick_counter += config.COST_CONTEXT_SWITCH
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
        if self.tick_counter == 15006:
            print("del")
        cur_task = self.cur_task

        cur_process_id = cur_task.process_id
        cur_process = self.processes[cur_process_id]

        # check if task was preempted and is in other slot
        if cur_task.was_preempted != 0:
            tasks_of_current_slot = cur_task.shares_slot_with[-1]
            instructions_planned = tasks_of_current_slot.length_plan_unchanged
        else:
            instructions_planned = cur_task.length_plan_unchanged

        instructions_planned_task = self.cur_task.length_plan_unchanged
        # --- calculate t1 ---
        self.thresholds['t1'] = thresholder.compute_t1(instructions_planned)
        self.thresholds['t1_pure'] = self.thresholds['t1'] - instructions_planned_task

        # --- calculate t2 ---
        t2_task = thresholder.compute_t2_task(instructions_planned_task, self.thresholds['t1'])
        self.thresholds['t2_task'] = t2_task
        self.thresholds['t2_task_pure'] = t2_task - instructions_planned_task
        t2_process = thresholder.compute_t2_process(cur_process, self.stress)
        self.thresholds['t2_process'] = t2_process
        planned_length_all_finished_tasks = sum(list([t.length_plan_unchanged for t in self.finished_tasks]))
        length_first_10 = sum(self.task_list[:10])
        ins_planned = length_first_10 if planned_length_all_finished_tasks < length_first_10 else planned_length_all_finished_tasks
        t2_node = thresholder.compute_t2_node(ins_planned)
        self.thresholds['t2_node'] = t2_node
        t2_preemptions = thresholder.compute_t2_preemptions(cur_task)
        self.thresholds['t2_preemptions'] = t2_preemptions

        # --- calculate tm2 ---
        tm2_task = thresholder.compute_tm2_task(instructions_planned_task, self.thresholds['t2_task'])
        self.thresholds['tm2_task'] = tm2_task
        self.thresholds['tm2_task_pure'] = tm2_task - instructions_planned_task
        tm2_node = thresholder.compute_tm2_node(self.thresholds['t2_node'])
        self.thresholds['tm2_node'] = tm2_node

        assert self.thresholds['t1'] > self.cur_task.length_plan_unchanged
        assert self.thresholds['t1'] < self.thresholds['t2_task']


    def has_finished(self) -> bool:
        return False if len(self.task_list) > 0 else True

    def mark_process_finished(self):
        """
        Marks the currently runnig process finished.
        Updates Process_list, updates number of planned_instructions
        :return:
        """
        assert len(self.cur_process.tasks) == 0
        self.processes.remove(self.cur_process)
        self.length_plan = sum([sum(process.tasks) for process in self.processes])
        raise NotImplementedError

    def search_task_following(self, cur_id) -> int:
        """
        Returns the index of the task that is following the task with the given id according to the plan
        """
        for i, t in enumerate(self.task_list):
            if t.task_id == cur_id:
                return i+1
        return len(self.task_list)

    def get_reference_point_for_task(self, task: Task) -> int:
        """
        Returns the time point the task given is compared to
        :param task: the task
        :return:
        """
        if task.is_running:
            return task.end_time
        else:
            raise NotImplementedError

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

        t2_process = self.thresholds['t2_process']

        t2_node = self.thresholds['t2_node']
        tm2_node = self.thresholds['tm2_node']

        cur_task_id = self.cur_task.task_id
        cur_task_len_unchanged = self.cur_task.length_plan_unchanged
        cur_task_len_plan = int(self.cur_task.length_plan)
        cur_task_len_real = self.cur_task.length_real
        lateness_task = self.cur_task.get_lateness_task()
        preemptions = self.cur_task.was_preempted
        cur_process_id = self.cur_process.process_id
        lateness_process = self.cur_process.lateness
        lateness = self.lateness_node

        line_thresholds = f'tick:{tick};t1_sum:{t1_sum};t1_pure:{t1_pure};t2_task_sum:{t2_task_sum};' \
                          f't2_task_pure:{t2_task_pure};t2_process:{t2_process};t2_node:{t2_node};' \
                          f'tm2_task_sum:{tm2_task_sum};tm2_task_pure:{tm2_task_pure};tm2_node:{tm2_node};'
        line_task = f'cur_task_id:{cur_task_id};cur_task_len_unchanged:{cur_task_len_unchanged};' \
                    f'cur_task_len_plan:{cur_task_len_plan};cur_task_len_real:{cur_task_len_real};' \
                    f'lateness_task:{lateness_task};preemptions:{preemptions};'
        line_rest = f'cur_process_id:{cur_process_id};lateness_process:{lateness_process};lateness_node:{lateness}'
        log_string = line_thresholds + line_task + line_rest + '\n'
        self.log_unified.write(log_string)

    def write_thresh_log(self):
        """
        Writes the current state of the thresholds to a file
        :return:
        """
        # format: cur_jobid cur_process_id cur_task_id cur_t1 cur_t2 cur_-t2
        if self.t1_pure < 0:
            print("lame")  # todo: t1 > 0
        assert self.t1_pure > 0
        assert self.t2_task_pure > 0
        assert self.tm2_task_pure < 0

        if self.cur_task.task_id != -1:
            self.log_thresh.write(
                f'{self.tick_counter} {self.cur_task.task_id} {self.t1} {self.t2} {self.t_m2}\n')
            self.log_thresh_pure.write(
                f'{self.tick_counter} {self.cur_task.task_id} {self.t1_pure} {self.t2_pure} {self.tm2_pure}\n')

        else:
            self.log_thresh.write(f'-1 0 0 0\n')  # empty space

    def write_tick_log(self):
        """
        Writes Task-Information and the current time to File
        FORMAT: Time [TASK]
        :return: None
        """
        self.tick_log.write(
            f'{self.tick_counter} {str(self.cur_task)}\n')

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

    def __repr__(self) -> str:
        return f"{{'lateness_node': {self.lateness_node}}}"
