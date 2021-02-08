

class Tracker:
    """
    Objects of this class keep track off all the stats that are required for threshold calculation and analysis
    """
    def __init__(self, number_processes, number_tasks, processes):
        """
        : param number_processes:  int, how many processes to track
        : param number_tasks: int, total number of tasks
        : param processes: [Process], all processes to track 
        """

        self.number_processes = number_processes
        self.number_tasks = number_tasks
        self.task_lists = [x.tasks for x in processes]

            # ---- PROCESS SPECIFIC TRACKING ----
        self.process_latenesses = [0 for x in range(number_processes)] # the individual buffer of a job
        self.process_buffers = [0 for x in range(number_processes)] # the individual buffers of a process
        self.process_buffer_allowence = [0 for x in range(number_processes)] # the individual allowence of a process
        self.instructions_planned_per_process = [sum(x) for x in self.task_lists] # the planned instructions per process
        self.instructions_done_per_process = [0 for x in range(number_processes)]


        # ---- PROCESS UNSPECIFIC TRACKING ----
        self.overall_lateness = 0 # time the whole node is late or early, aka accumulated lateness
        self.lateness_per_task = [0 for x in range(self.number_tasks)] # lateness per task, indice is task_id
        self.instructions_planned_all = sum(self.instructions_planned_per_process)
        self.instructions_planned_left = sum(self.instructions_planned_per_process)
        self.instructions_done_all = 0
        self.stress = 0
        self.time_instructions = 0 # keeps time of the instructions passed
        self.cur_tick = 0

    def run_tick(self, ins: int):
        self.time_instructions += ins
        self.instructions_done_all += ins
        self.instructions_planned_left -= ins
        self.cur_tick += 1

    def update_lateness(self, process_id):
        # TODO: REQUIRED?!? Prob no
        pass

    def run_tick_sleep(self, ins:int):
        self.time_instructions += ins

    def add_lateness_to_task(self, task_id, ins):
        try:
            self.lateness_per_task[task_id] += ins
        except IndexError:
            print("index_error_id:", task_id)
            print("length lateness_per_pask", len(self.lateness_per_task))
            assert False


    def add_lateness_to_process(self, process_id, ins):
        self.process_latenesses[process_id] += ins

    def get_time_instructions(self) -> int:
        return self.time_instructions

    def update_buffer(self, process_id, ins):
        """
        Changes buffer with the given instructions, default is assumed to be lateness, so negative ins parameter increases buffer
        """
        self.process_buffers[process_id] -= ins

    def instructions_left_per_process(self, process_id: int) -> int:
        left = self.instructions_planned_per_process[process_id] - self.instructions_done_per_process[process_id]
        return left

    def add_process_lateness(self, id: int, ins: int):
        """
        Tracks the lateness per individual process but accumutavly also keeps track of overall lateness too
        """
        self.overall_lateness += ins
        self.process_lateness[id] += ins

    def get_process_lateness(self, id: int) -> int:
        return self.process_latenesses[id]

    def get_overall_lateness(self) -> int:
        return self.overall_lateness

    def update_overall_lateness(self, ins):
        self.overall_lateness += ins

    def get_instrcutions_planned_per_p(self, id):
        return self.instructions_planned_per_process[id]

    def get_current_tick(self) -> int:
        # returns current tick of simulation as increments of start value 0
        return self.cur_tick
