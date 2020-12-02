from typing import List
from task import Task
from process import Process
from thresholder import Threshold
from tracking import Tracker
from vrm import VRM
from plan import Plan

log = False

class ProcessRunner:
    def __init__(self, plan, tick_log="logs/tick.log", ipt=1, log=False):
        assert type(plan) is Plan

        self.ipt: int = ipt
        self.plan: List[Task] = plan.task_list
        self.processes: List[Process] = plan.processes
        self.number_processes:int = len(self.processes)
        self.number_tasks = plan.number_all_tasks
        self.tracking = Tracker(self.number_processes, self.number_tasks, self.processes)
        self.thresholds = [Threshold(p) for p in self.processes]
        self.cur_task = self.plan[0]
        self.cur_process = self.processes[self.cur_task.process_id]
        self.cur_process_id = self.cur_process.process_id
        self.finished_tasks = 0
        self.vrm = VRM(self.plan)

        if log is True:
            self.thresh_log = open(tick_log, 'w')
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
        ins = self.ipt
        cur_task.run(ins)

        if cur_task.finshed_early:
            early_instructions = cur_task.get_early_instructions()
            self.tracking.add_lateness_to_task(cur_task.task_id, -1* early_instructions)
            self.tracking.add_lateness_to_process(cur_process.process_id, -1* early_instructions)
            self.tracking.update_overall_lateness(-1*early_instructions)
            self.tracking.update_buffer(cur_process.process_id, -1*early_instructions)

        if cur_task.is_late:
            late_instructions = cur_task.get_late_instructions(ins)
            self.tracking.add_lateness_to_task(cur_task.task_id, late_instructions)
            self.tracking.add_lateness_to_process(cur_process.process_id, late_instructions)
            self.tracking.update_buffer(cur_process.process_id, late_instructions)

        if cur_task.task_finished:
            ipt_left = cur_task.get_overdone_instructions()
            cur_process.run_task(cur_task.task_id, ins - ipt_left)
            self.pick_next_task()
            cur_task = self.cur_task
            cur_task.run(ipt_left)



        if log:
            self.log_thresh()
            self.log_tick()

        self.tracking.run_tick(self.ipt)
        self.update_thresholds()

        #TODO: RUN instructions on process with exact amount of actual done instructions

    def preempt_current_process(self):
        """
        preempts the currently running task, inserts the remaining part where the next task of the process would start and starts the next process
        """
        insert_index = None
        next_task_index = 1
        next_task = plan[next_task_index]
        # we look for a slot in the plan that either is assigned to the same process id or is free (=> -1)
        while next_task.process_id != self.cur_task.process_id or next_task.process_id != -1:
            next_task_index += 1
            try:
                next_task = plan[next_task_index]
            except IndexError:
                print("task was last task")

        self.plan.insert(next_task_index, self.cur_task)
        self.plan = self.plan[1:]
        self.cur_task = self.plan[0]


    def singal_prediction_failure(self):
        """
        Should signal to the VRM that there is an significant failure with the prediction of the prediction model.
        In this simulation this step is kept very simple
        """

    def pick_next_task(self):
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
        cur_thresh.update_thresholds(instructions_left=left, instructions_planned=planed, cur_task=cur_task)

    def has_finished(self) -> bool:
        return False if len(self.plan) > 0 else True

    def write_plan_to_file(self, path):
        meta = f'{len(self.processes)};'
        # meta = f'{len(self.processes)},{len(self.plan)};;'
        for i,p in enumerate(self.processes):
            meta += f'{i},{i},{p.buffer};'

        tasks_s = ''
        for task in self.plan:
            tasks_s += f'{task.process_id},{task.process_id},{task.task_id},{task.length_plan},{task.length_real};'

        plan_s = meta + ";;" + tasks_s

        with open(path, 'w') as f:
            f.write(plan_s)
            # now again in human readable ;)
            f.write('\n\n#########\n\n')
            for task in self.plan:
                f.write(f'{task.process_id} {task.process_id} {task.task_id} {task.length_plan} {task.length_real}\n')

    def log_thresh(self):
        if log is False:
            return
        cur_p = self.cur_process.process_id
        cur_t = self.thresholds[cur_p]
        self.thresh_log.write(f'{self.cur_task.task_id} {cur_t["t1"]} {cur_t["t2"]} {cur_t["t_minus2"]}\n')


    def log_tick(self):
        self.thresh_log.write(str(self.cur_task) + '\n')



    def __del__(self):
        if log is False:
            return
        self.thresh_log.close()
