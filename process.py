from task import Task

ipt = None # instructions per tick
load = None #
log = False
hz = None
max_buff_usg = 0
ticks_off = 1
reschedule_time = 0
max_task_deviation = None
max_task_overstep = None # depending on the general lateness on the node, this value will be adjusted


# --- CLASS ---
class Process:
    def __init__(self, tasks: Task, buffer: int, deadline: int):
        """
        Representation of a process on a node.
        Params:
            tasks: List of Tasks
            buffer: number of instructions from end of last task to deadline
            deadline: Deadline in instruction, counting from 0 at start
        """
        # global
        self.load = load # systemload
        self.hz = hz
        self.ipt = ipt
        self.log = log
        self.max_buff_usg = max_buff_usg

        # state keeping process
        self.tasks_plan = tasks # list of all tasks
        self.cur_task = self.tasks_plan[0] # currently running task
        self.cur_task_length_plan = self.cur_task.length_plan # the originally tracked length of plan
        self.buffer = int(buffer) # whole buffer in instructions
        self.buffer_allowence = 0
        self.lateness_process = 0
        self.lateness_task = 0
        self.instructions_sum = sum(self.tasks_plan)
        self.instructions_left = sum(self.tasks_plan)
        self.instructions_done = 0
        self.process_id = self.cur_task.process_id
        self.finished_process = False
        self.DEADLINE = deadline # last task time + buffer
        self.max_task_overstep = max_task_overstep

        # thresholds
        self.t1 = 0
        self.t2 = 0
        self.t_minus2 = 0
        self.stress = 1 # static atm
        self.reschedule_time = reschedule_time
        self.threshold_state = 0 # holds the current state of the threshold
        self.max_task_deviation = max_task_deviation
        self.ticks_off = ticks_off
        self.thresh_flag = None # remembers by which component of the formular the threshold is defined

        # admin
        self.log_thresh = open(f'logs/thresh_{self.process_id}.log', 'w')
        self.log_thresh_pure = open(f'logs/pure_{self.process_id}.log', 'w') # logging of the pure instruction amount that is been granted

    def run_task(self, task_id, ins):
        '''
        updates the state of the task list
        '''
        self.update_lateness()
        self.update_thresholds()
        if self.cur_task.length_real <= 0:
            self.tasks_plan = self.tasks_plan[1:]
            if len(self.tasks_plan) == 0:
                self.finished_process = True
                return
            self.cur_task = self.tasks_plan[0]
            self.cur_task_length_plan = self.cur_task.length_plan
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
        self.t1 = self.calc_t1(self.cur_task_length_plan)
        self.t2 = self.calc_t2(buffer_allowence)
        self.t_minus2 = self.calc_t_minus(self.cur_task.length_plan)

        if self.log is True:
            self.log_thresh.write(f'{self.cur_task.task_id} {self.t1} {self.t2} {self.t_minus2}\n')
            self.log_thresh_pure.write(f'{self.cur_task.task_id} {self.t1 - self.cur_task_length_plan} {self.t2 - self.cur_task_length_plan} {self.t_minus2}\n')

    def calc_t1(self, instructions_planned) -> int:
        max_dev = self.max_task_deviation * instructions_planned
        max_overreach = instructions_planned + self.max_task_overstep
        t1 = int(min(max_dev, max_overreach))
        print("max_dev") if max_dev < max_overreach else print("max_overreach")
        assert t1 > 0

        return t1

    def calc_t2(self, buffer_allowence) -> int:
        # TODO: static threshhold depending on stress level
        allowence_relative = self.t1 + buffer_allowence - self.reschedule_time
        return int(self.t1 + buffer_allowence - self.reschedule_time)

    def calc_t_minus(self, instructions_planned):
        return int(-1 * self.t2 * 2)

    def __del__(self):
        self.log_thresh.close()

    def update_stress(self, change: int):
        pass # TODO: implement; change max_task_overstep
