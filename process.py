ipt = None # instructions per tick
load = None #
log = False
hz = None
max_buff_usg = 0
ticks_off = 1
reschedule_time = 0
max_task_deviation = 0


# --- CLASS ---
class Threshold:
    def __init__(self, tasks, buffer):
        # global
        self.load = load # systemload
        self.hz = hz
        self.ipt = ipt
        self.log = log
        self.max_buff_usg = max_buff_usg

        # state keeping process
        self.tasks_plan = tasks
        self.cur_task = self.tasks_plan[0]
        self.buffer = int(buffer) # whole buffer in instructions
        self.buffer_allowence = 0
        self.lateness_process = 0
        self.lateness_task = 0
        self.instructions_sum = sum(self.tasks_plan)
        self.instructions_left = sum(self.tasks_plan)
        self.instructions_done = 0
        self.process_id = self.cur_task.process_id
        self.finished_process = False

        # thresholds
        self.t1 = 0
        self.t2 = 0
        self.t_minus2 = 0
        self.stress = 1 # static atm
        self.reschedule_time = reschedule_time
        self.threshold_state = 0 # holds the current state of the threshold
        self.max_task_deviation = max_task_deviation
        self.ticks_off = ticks_off

        # admin
        self.log_thresh = open(f'thresh_{self.process_id}.log', 'w')


    def run_task(self, task_id, ins):
        '''
        updates the state of the task list
        '''
        #    import pdb; pdb.set_trace()

        self.update_lateness()
        self.update_thresholds()
        if self.cur_task.length_real <= 0:
            self.tasks_plan = self.tasks_plan[1:]
            if len(self.tasks_plan) == 0:
                self.finished_process = True
                return
            self.cur_task = self.tasks_plan[0]
            self.lateness_task = 0


        self.instructions_done += ins
        self.instructions_left -= ins

        self.threshold_state = self.check_thresholds()


    def update_lateness(self):
        # task is on time
        if self.cur_task.length_plan > 0:
            return
        # tasks turns late
        elif self.cur_task.length_plan < 0 and self.cur_task.late is False:
            self.lateness_task += self.cur_task.length_plan
            self.lateness_process += self.cur_task.length_plan
            self.cur_task.late = True
        elif self.cur_task.length_plan < 0 and self.cur_task.late is True:
            self.lateness_task += self.ipt
            self.lateness_process += self.ipt


    def check_thresholds(self) -> int:
        if self.lateness_task < self.t1:
            return 0
        elif self.lateness_task > self.t1:
            return 1
        elif self.lateness_process > self.t2:
            return 2
        else:
            return -1

    def update_thresholds(self):
        buffer_allowence = self.instructions_left/self.instructions_sum * self.buffer * self.load
        self.t1 = self.calc_t1(self.cur_task.length_plan)
        self.t2 = self.calc_t2(buffer_allowence)
        self.t_minus2 = self.calc_t_minus(self.cur_task.length_plan)

        if self.log is True:
            self.log_thresh.write(f'{self.cur_task.task_id} {self.t1} {self.t2} {self.t_minus2}\n')


    def calc_t1(self, instructions_planned) -> int:
        return int(min(max(instructions_planned * self.max_task_deviation, instructions_planned + self.ipt * self.ticks_off), self.max_task_deviation * instructions_planned))

    def calc_t2(self, buffer_allowence) -> int:
        # TODO: static threshhold depending on stress level
        return int(self.t1 + buffer_allowence - self.reschedule_time)

    def calc_t_minus(self, instructions_planned):
        return int(-1 * self.t2 * 2)

    def __del__(self):
        self.log_thresh.close()

class ProcessRunner:
    def __init__(self, plan, processes):
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
            self.log = open('log', 'w')


    def run_tick(self):
        '''
        Runs the simulation.
        '''
        assert self.cur_task.length_real > 0

        finished = self.cur_task.run(self.ipt)

        # current task has still instructions left
        if finished == 1:
            if self.cur_process.threshold_state == 0:
                return
            elif self.cur_process.threshold_state == 1:
                self.preempt_current_process()
            elif self.cur_process.threshold_state == 2:
                self.singal_prediction_failure()

        self.cur_process.run_task(self.cur_task.task_id, self.ipt)
        # the current task was finished
        if finished < 0:
            self.cur_task.task_finished = True
            self.pick_next_task()
            self.cur_task.run(finished * -1)
            self.cur_process.run_task(self.cur_task.task_id, self.ipt)
            print(f'task {self.finished_tasks} finished')
            self.finished_tasks += 1
        self.log.write(str(self.cur_task) + '\n')
        self.tick += 1

        #TODO: RUN instructions on process with exact amount of actual done instructions

    def preempt_current_process(self):
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

        buff_list = ''
        for i,p in enumerate(self.processes):
            buff_list += f'{i} {p.buffer},'

        tasks_s = ''
        for task in self.plan:
            tasks_s += f'{task.process_id} {task.process_id} {task.task_id} {task.length_plan} {task.length_real};'

        meta_s = f'{len(self.plan)} HERE_LENGTH'

        task_list = meta_s + ';;;' + tasks_s
        plan_s = buff_list + ";;;" + task_list

        with open(path, 'w') as f:
            print(plan_s)
            f.write(plan_s)
