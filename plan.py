from random import randint
from copy import deepcopy
from task import Task
from typing import List, Set, Dict, Tuple, Optional


class Plan:
    def __init__(self, processes: Tuple[int, int], task_list: List[Task]):
        self.process_info = processes # list of tuples [(task_list_p0, buffer_p0, deadline_p0),(task_list_p1, buffer_p1, deadline_p0),...]
        self.task_list = task_list # [task0,]
        self.number_tasks_per_process = self.get_number_tasks() # last number is amount of free slots

    @staticmethod
    def generate_plan(num_processes, min_len_p, max_len_p, min_len_task, max_len_task, min_buffer, max_buffer, free_time, file_path=None) -> 'Plan':
        """
        Produces a plan according to the given parameters. The process with the id -1 stands for freely available time.
        len_p: total amount of tasks per process
        len_task: instructions per task
        buffer: % of total length that is available as buffer
        free_time: %*100 of total time that is not assigned
        """
        # calc amount of tasks for each process
        process_length = [[] for x in range(num_processes)]
        for p in range(num_processes):
            process_length[p] = randint(min_len_p, max_len_p)
            print(f'[PLAN] Process {p} has {process_length[p]} tasks')


        # create tasks for each process
        tasks_per_process = [[] for x in range(num_processes)] # [[taks0 of p0, task1 of p0],[task2 of p1]...]
        cur_id = 0
        sum_process_length = [] # list of ints describing sum of instructions per process
        for cur_process in range(num_processes):
            for i in range(process_length[cur_process]):
                tasks_per_process[cur_process].append(Task(randint(min_len_task,max_len_task), cur_process, cur_id))
                cur_id += 1
            sum_process_length.append(sum([x.length_plan for x in tasks_per_process[cur_process]]))

        # create plan out of tasks for each process
        plan = []
        sum_tasks = 0
        for p in tasks_per_process:
            sum_tasks += len(p)
        print(f'[PLAN] generated {sum_tasks} tasks')
        all_pro_and_tasks = deepcopy(tasks_per_process)
        free_slots = Plan.generate_free_slots(free_time, sum_tasks, min_len_task, max_len_task)
        sum_tasks += len(free_slots)
        all_pro_and_tasks.append(free_slots)

        plan = Plan.generate_realistic_plan(all_pro_and_tasks, sum_tasks)

        # calc buffers
        buffer_list = []
        for p in tasks_per_process:
            sum_instructions = 0
            for t in p:
                sum_instructions += t.length_plan
            buffer_list.append(sum_instructions*(randint(min_buffer,max_buffer)/100))

        # calc deadlines
        plan.reverse() # so ids are increasing
        last_tasks_of_process_finish = Plan.find_last_task_ending(plan, num_processes)
        deadlines = []
        for p, last_task_finish in enumerate(last_tasks_of_process_finish):
            deadlines.append(last_task_finish + buffer_list[p])

        # create plan data types
        processes = []
        for i in range(len(process_length)):
            processes.append((tasks_per_process[i], int(buffer_list[i]), deadlines[i]))



        assert len(processes) == len(process_length)
        assert len(plan) == sum_tasks + len(free_slots)

        if file_path is not None:
            with open(file_path, 'w') as f:
                for t in plan:
                    f.write(str(t)+'\n')
        print(f'plan with {len(plan)} tasks created')
        return Plan(processes, plan)

    @staticmethod
    def generate_realistic_plan(processes: List[List[Task]], sum_tasks: int) -> List[Task]:
        """
        Mixes up the plan in such a way that there is some kind of meaningful switching between tasks for different processes/jobs
        """
        num_processes = len(processes)
        cur_id = 0
        plan = []
        last_picked = None

        for task_id in range(sum_tasks):
            new_task = None

            while new_task is None:
                process_to_pick_from = randint(0, num_processes) -1
                try:
                    if process_to_pick_from == last_picked and num_processes > 0:
                        continue
                    else:
                        new_task = processes[process_to_pick_from].pop()
                        last_picked = process_to_pick_from
                except IndexError:
                    processes = [x for x in processes if x]
                    num_processes -= 1
            plan.append(new_task)
        return plan


    @staticmethod
    def generate_free_slots(free_slot_chance: int, number_tasks: int, min_len: int, max_len: int) -> List[Task]:
        """
        generates a list of free slosts according to chance in FREE_TIME in proportion to number_tasks
        """
        free_slots_num = int(number_tasks / free_slot_chance)
        free_slots = []
        PROCESS_TASK_ID = -1
        for free in range(free_slots_num):
            length = randint(min_len, max_len)
            new_task = Task(length, PROCESS_TASK_ID, PROCESS_TASK_ID)
            free_slots.append(new_task)
        return free_slots


    @staticmethod
    def find_last_task_ending(plan: List[Task], num_processes: int) -> List[int]:
        """
        Returns the finishing time for each process
        """
        instr_counter = 0
        latest_task = [[] for x in range(num_processes)] # holds finishing time for latest task of each process
        for task in plan:
            instr_counter += task.length_plan
            if task.task_id == -1:
                continue
            latest_task[task.process_id] = instr_counter
        print(latest_task)
        return latest_task


    def get_number_tasks(self) -> list:
        lenghts = []
        for process in self.process_info:
            lenghts.append(process[0])
        lenghts.append(0)
        for el in self.task_list:
            if el.task_id == -1:
                lenghts[-1] += 1
        return lenghts




    @staticmethod
    def pick_next_task(all_pro_and_tasks):
        return all_pro_and_tasks[process_to_pick].pop()
