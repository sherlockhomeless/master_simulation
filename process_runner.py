from task import Task

ipt = None # instructions per tick

class ProcessRunner:
    def __init__(self, plan, processes, tick_log="logs/tick.log"):
        global ipt
        global log
        self.ipt = ipt
        self.plan = plan
        self.processes = processes
        self.stress = 0
        self.cur_task = plan[0]
        self.cur_process = processes[self.cur_task.process_id]
        self.tick = 0
        self.finished_tasks = 0
        if log is True:
            self.thresh_log = open(tick_log, 'w')


    def run_tick(self):
        '''
        Simulates the equivalent of an timer tick. Updates the Threshold and executes the appropriate actions if a threshold is transgressed
        '''
        assert self.cur_task.length_real > 0

        finished = self.cur_task.run(self.ipt)
        self.cur_process.run_task(self.cur_task.task_id, self.ipt)
        if log:
            self.log_thresh()

        # the current task was not finished
        if finished == 1:
            if self.cur_process.threshold_state == 0: # current task has still instructions left
                return
            elif self.cur_process.threshold_state == 1: # current task has still instructions left but transgressed into t1
                self.preempt_current_process()
            elif self.cur_process.threshold_state == 2: # current task has still instructions left but transgressed into t2
                self.singal_prediction_failure()

        # the current task was finished
        else:
            self.cur_task.task_finished = True
            self.pick_next_task()
            self.cur_task.run(finished * -1)
            self.cur_process.run_task(self.cur_task.task_id, self.ipt)
            print(f'task {self.finished_tasks} finished')
            self.finished_tasks += 1

        self.thresh_log.write(str(self.cur_task) + '\n')
        self.tick += 1

        #TODO: RUN instructions on process with exact amount of actual done instructions

    def preempt_current_process(self):
        def ## TODO: IMPLEMENT INTERNE METHODEN

        pass #TODO: Implement

    def singal_prediction_failure(self):
        pass #TODO: Implement

    def pick_next_task(self):
        self.plan = self.plan[1:]
        if len(self.plan) == 0:
            return
        self.cur_task = self.plan[0]
        self.cur_process = self.processes[self.cur_task.process_id]

    def run(self):
        while self.has_finished is False:
            self.run_tick()

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
        cp = self.cur_process
        self.thresh_log.write(f'{cp.cur_task.task_id} {cp.t1} {cp.t2} {cp.t_minus2}\n')
