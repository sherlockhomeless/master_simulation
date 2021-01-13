from random import randint
from copy import deepcopy
from task import Task
from process import Process
from typing import List, Set, Dict, Tuple


class Plan:
    def __init__(self, task_list: List[Task], processes: List[Process]):
        assert type(processes) is list
        assert type(processes[0]) is Process

        self.processes = processes # [Process, Process]
        self.task_list = task_list # [task0,task1,task2]

        self.number_tasks_per_process = self.get_number_tasks_per_p() # last number is amount of free slots
        self.number_all_tasks = self.get_number_all_tasks()

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


        tasks_per_process = Plan.generate_tasks_for_processes(list(process_length), min_len_task, max_len_task)

        # create plan out of tasks for each process
        plan = []
        sum_tasks = 0
        for p in tasks_per_process:
            sum_tasks += len(p)
        print(f'[PLAN] generated {sum_tasks} actual tasks')
        all_pro_and_tasks = deepcopy(tasks_per_process)
        free_slots = Plan.generate_free_slots(free_time, sum_tasks, min_len_task, max_len_task)
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
        #plan.reverse() # so ids are increasing
        last_tasks_of_process_finish = Plan.find_last_task_ending(plan, num_processes)
        deadlines = []
        for p, last_task_finish in enumerate(last_tasks_of_process_finish):
            deadlines.append(last_task_finish + buffer_list[p])

        # create plan data types
        processes = []
        for i in range(len(process_length)):
            processes.append(Process(tasks_per_process[i], int(buffer_list[i]), deadlines[i]))


        assert len(processes) == len(process_length)
        try:
            assert len(plan) == sum_tasks + len(free_slots)
        except Exception as e:
            print(len(plan), sum_tasks, len(free_slots))
            assert False

        if file_path is not None:
            with open(file_path, 'w') as f:
                for t in plan:
                    f.write(str(t)+'\n')

        print(f'plan with {len(plan)} tasks created')
        return Plan(plan, processes)

    @staticmethod
    def generate_realistic_plan(processes: List[List[Task]], sum_tasks: int) -> List[Task]:
        """
        Mixes up the plan in such a way that there is some kind of meaningful switching between tasks for different processes/jobs. The Task-List on the last index is for free slots
        """
        num_processes = len(processes)
        cur_id = 0
        plan = []
        last_picked = None

        for cur_task_id in range(sum_tasks):
            found = False
            for p in processes:
                if found is True:
                    break
                for t in p:
                    if t.task_id == cur_task_id:
                        plan.append(t)
                        found = True
                        break
        # now we got a plan with increasing task-ids, now insert free slots
        for free_slot in processes[-1]:
            insert_index = randint(1, len(plan)-1)
            plan.insert(insert_index, free_slot)
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
        print(f'[PLAN] have {free_slots_num} free slots')
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
        return latest_task

    @staticmethod
    def generate_tasks_for_processes(length_per_process: List[int], min_len, max_len):
        """
        Takes a List of integers that describe the tasks per process (index == process_id) and generates a list of tasks matching the length given by the integer
        """

        num_processes = len(length_per_process)
        tasks_per_process = [[] for x in range(num_processes)]
        cur_id = 0
        last_process_id = -1
        next_task_process_id = 0
        while(length_per_process != []):
            cur_length = len(length_per_process)
            # --- pick next process-id
            while(next_task_process_id == last_process_id):
                next_task_process_id = randint(0,cur_length-1)
                if len(length_per_process) == 1:
                    next_task_process_id = 0
                    break
            # --- pick next task
            tasks_per_process[next_task_process_id].append(Task(randint(min_len,max_len), next_task_process_id, cur_id))
            # --- setup for next run
            cur_id += 1
            length_per_process[next_task_process_id] -= 1
            if length_per_process[next_task_process_id] == 0:
                length_per_process.remove(0)
            last_process_id = next_task_process_id

        assert len(length_per_process) == 0
        return tasks_per_process

    def get_number_tasks_per_p(self) -> list:
        """
        Returns the number of tasks per Process.
        """
        lenghts = []
        for process in self.processes:
            lenghts.append(len(process))
        lenghts.append(0)
        for el in self.task_list:
            if el.task_id == -1:
                lenghts[-1] += 1
        return lenghts


    def get_number_all_tasks(self) -> int:
        counter = 0
        for task in self.task_list:
            if task.process_id != -1:
                counter += 1
        return counter

    @staticmethod
    def pick_next_task(all_pro_and_tasks):
        return all_pro_and_tasks[process_to_pick].pop()
