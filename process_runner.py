from typing import List
from task import Task
from process import Process
from thresholder import Threshold
from tracking import Tracker
from vrm import VRM
from plan import Plan


log = False
COST_CONTEXT_SWITCH = None


class ProcessRunner:
    def __init__(self, plan, tick_log="logs/tick.log", thresh_log="logs/per_tick_thresh_sum.log", thresh_log_pure="logs/per_tick_thresh_pure.log", ipt=1, log=False, breakpoint=None):
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

        self.ipt: int = ipt
        self.plan: List[Task] = plan.task_list
        self.processes: List[Process] = plan.processes
        self.number_processes: int = len(self.processes)
        self.number_tasks = plan.number_all_tasks
        self.tracking = Tracker(self.number_processes,
                                self.number_tasks, self.processes)
        self.thresholds = [Threshold(p) for p in self.processes]
        self.cur_task = self.plan[0]
        self.cur_process = self.processes[self.cur_task.process_id]
        self.cur_process_id = self.cur_process.process_id
        self.finished_tasks = 0
        self.vrm = VRM(self.plan)
        self.time = 0

        if log is True:
            self.tick_log = open(tick_log, 'w')
            self.log_thresh = open(thresh_log, 'w')
            self.log_thresh_pure = open(thresh_log_pure, 'w')
        else:
            self.thresh_log = open('/dev/null', 'w')

    def run_tick(self):
        '''
        Simulates the equivalent of an timer tick. Updates the Threshold and executes the appropriate actions if a threshold is transgressed
        '''

        # --- update on task & process level ---
        assert self.cur_task.length_real > 0

        cur_task = self.cur_task
        cur_process = self.cur_process
        cur_process_id = cur_process.process_id
        cur_task_id = cur_task.task_id
        cur_thresholds = self.thresholds[cur_process_id]
        ins = self.ipt
        # runs the full set of instructions on the current task
        cur_task.run(ins)


        if cur_task.has_task_finished():
            instructions_left_in_tick = cur_task.get_overdone_instructions()

            if cur_task.has_task_finished_early():
                current_t_m2 = cur_thresholds.t_minus2
                earliness = cur_task.get_early_instructions(instructions_left_in_tick)
                if earliness < current_t_m2:
                    self.vrm.signal_t_m2(earliness, cur_process_id, cur_task_id)

            self.pick_next_task()
            cur_task.run(instructions_left_in_tick)

        elif cur_task.is_task_late():
            cur_t1, cur_t2 = cur_thresholds.t1, cur_thresholds.t2
            raise NotImplementedError





        # if cur_task.finshed_early:
        #     early_instructions = cur_task.get_early_instructions()
        #     self.tracking.add_lateness_to_task(
        #         cur_task.task_id, -1 * early_instructions)
        #     self.tracking.add_lateness_to_process(
        #         cur_process.process_id, -1 * early_instructions)
        #     self.tracking.update_overall_lateness(-1*early_instructions)
        #     self.tracking.update_buffer(
        #         cur_process.process_id, -1*early_instructions)
        #
        # if cur_task.is_late:
        #     late_instructions = cur_task.get_late_instructions(ins)
        #     self.tracking.add_lateness_to_task(
        #         cur_task.task_id, late_instructions)
        #     self.tracking.add_lateness_to_process(
        #         cur_process.process_id, late_instructions)
        #     self.tracking.update_buffer(
        #         cur_process.process_id, late_instructions)
        #     # continue here
        #
        # if cur_task.task_finished:
        #     ipt_left = cur_task.get_overdone_instructions()
        #     cur_process.run_task(cur_task.task_id, ins - ipt_left)
        #     self.pick_next_task()
        #     cur_task = self.cur_task
        #     cur_task.run(ipt_left)
        #     self.cur_process_id = cur_task.process_id
        #     print(
        #         f'[PROCESS_RUNNER] starting next task {self.cur_task.task_id}')

        self.tracking.run_tick(self.ipt)
        self.update_thresholds()

        if cur_task.is_late and self.transgresses_t1():
            self.preempt_current_process()

        if log:
            self.write_thresh_log()
            self.write_tick_log()

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
        [TODO] Supress another instant preemption
        [TODO] Let process only run amount of time that other task has available
        """
        cur_task_id = self.cur_task.task_id
        cur_process_id = self.cur_task.process_id
        next_task_index = self.search_task_following(cur_task_id)
        next_task = self.plan[next_task_index]
        # we look for a slot in the plan that either is assigned to the same process id or is free (=> -1)
        while next_task.process_id != self.cur_task.process_id or next_task.process_id != -1:
            try:
                next_task_index += 1
                next_task = self.plan[next_task_index]
            except IndexError:
                print("task was last task")

        self.plan.insert(next_task_index, self.cur_task)
        self.plan = self.plan[1:]
        self.cur_task = self.plan[0]
        print(f'Task ({cur_process_id},{cur_task_id}) was moved to plan index {next_task_index} before ({self.plan[next_task_index+1].process_id},{self.plan[next_task_index+1].task_id}) ')

    def singal_prediction_failure(self):
        """
        Should signal to the VRM that there is an significant failure with the prediction of the prediction model.
        In this simulation this step is kept very simple
        """

    def pick_next_task(self):
        """
        : param instructions_left: int, number of instructions left in current tick
        Picks the next task
        ! shortens the plan
        """
        self.plan = self.plan[1:]
        if len(self.plan) == 0:
            return
        self.cur_task = self.plan[0]
        self.cur_process = self.processes[self.cur_task.process_id]


    def run(self):
        while self.has_finished is False:
            self.run_tick()

    def update_thresholds(self):
        cur_pid = self.cur_process.process_id
        cur_task = self.cur_task

        cur_thresh = self.thresholds[cur_pid]
        left = self.tracking.instructions_left_per_process(cur_pid)
        planed = self.tracking.get_instrcutions_planned_per_p(cur_pid)
        cur_thresh.update_thresholds(
            instructions_left=left, instructions_planned=planed, cur_task=cur_task)
        if log:
            self.write_thresh_log()

    def has_finished(self) -> bool:
        return False if len(self.plan) > 0 else True

    def search_task_following(self, cur_id) -> int:
        """
        Returns the index of the task that is following the task with the given id according to the plan
        """
        for i, t in enumerate(self.plan):
            if t.task_id == cur_id:
                return i
        return len(self.plan)

    def write_plan_to_file(self, path):
        meta = f'{len(self.processes)};'
        # meta = f'{len(self.processes)},{len(self.plan)};;'
        for i, p in enumerate(self.processes):
            meta += f'{i},{i},{p.buffer},{p.deadline};'

        tasks_s = ''
        for task in self.plan:
            tasks_s += f'{task.process_id},{task.process_id},{task.task_id},{task.length_plan},{task.length_real};'

        plan_s = meta + ";;" + tasks_s

        with open(path, 'w') as f:
            f.write(plan_s)
            # now again in human readable ;)
            f.write('\n\n#########\n\n')
            for task in self.plan:
                f.write(
                    f'{task.process_id} {task.process_id} {task.task_id} {task.length_plan} {task.length_real}\n')

    def write_thresh_log(self):
        # format: cur_jobid cur_process_id cur_task_id cur_t1 cur_t2 cur_-t2
        cur_thresh = self.thresholds[self.cur_process_id]
        if self.cur_task.task_id != -1:
            self.log_thresh.write(
                f'{self.cur_task.task_id} {cur_thresh["t1"]} {cur_thresh["t2"]} {cur_thresh["t_minus2"]}\n')
            self.log_thresh_pure.write(
                f'{self.cur_task.task_id} {cur_thresh["t1_pure"]} {cur_thresh["t2_pure"]} {cur_thresh["t_minus2_pure"]}\n')

        else:
            self.log_thresh.write('-1 0 0 0\n')  # empty space

    def write_tick_log(self):
        self.tick_log.write(
            f'{str(self.cur_task)} {self.tracking.get_current_tick()} \n')

    def __del__(self):
        if log is False:
            return
        self.tick_log.close()

    @staticmethod
    def get_process_runner(new_plan):
        return ProcessRunner(new_plan)
