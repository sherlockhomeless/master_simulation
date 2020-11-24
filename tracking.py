

class Tracker:
    """
    Objects of this class keep track off all the stats that are required for threshold calculation and analysis
    """
    def __init__(self, number_processes, number_tasks, processes):
        self.number_processes = number_processes
        self.number_tasks = number_tasks
        self.task_lists = [x.tasks_plan for x in processes]

            # ---- PROCESS SPECIFIC TRACKING ----
        self.process_latenesses = [[] for x in range(number_processes)] # the individual buffer of a job
        self.process_buffers = [[] for x in range(number_processes)] # the individual buffers of a process
        self.process_buffer_allowence = [[] for x in range(number_processes)] # the individual allowence of a process
        self.instructions_planned_per_process = [sum(x) for x in self.task_lists] # the planned instructions per process
        self.instructions_done_per_process = [[0] for x in range(number_processes)]


        # ---- PROCESS UNSPECIFIC TRACKING ----
        self.overall_lateness = 0 # time the whole node is late or early, aka accumulated lateness
        self.lateness_per_task = [[] for x in range(self.number_tasks)] # lateness per task, indice is task_id
        self.instructions_planned_all = sum(self.instructions_planned_per_process)
        self.instructions_done_all = 0
        self.stress = 0
        self.time_instructions = 0 # keeps time of the instructions passed

    def run_tick(self, ins: int):
        self.time_instructions += ins

    def get_time_instructions() -> int:
        return self.time_instructions

    def add_process_lateness(self, id: int, ins: int):
        """
        Tracks the lateness per individual process but accumutavly also keeps track of overall lateness too
        """
        self.overall_lateness += ins
        self.process_lateness[id] += ins

    def get_process_lateness(self, id: int) -> int:
        return self.process_latenesses[id]

    def get_overall_lateness(self) -> int:
        return self.process_latenesses
