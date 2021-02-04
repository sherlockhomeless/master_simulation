from random import randint, choice
from copy import deepcopy
from task import Task
from process import Process
from typing import List, Set, Dict, Tuple


class Plan:
    def __init__(self, task_list: List[Task], processes: List[Process]):
        assert type(processes) is list
        assert type(processes[0]) is Process

        self.processes = processes  # [Process, Process]
        self.task_list = task_list  # [task0,task1,task2]

        # last number is amount of free slots
        self.number_tasks_per_process = self.get_number_tasks_per_p()
        self.number_all_tasks = self.get_number_all_tasks()
        self.number_all_proceses = len(self.processes)

    @staticmethod
    def generate_plan(num_processes, min_len_process, max_len_process, min_len_task, max_len_task, min_buffer, max_buffer, free_time, file_path=None) -> 'Plan':

        assert free_time >= 0
        # --- generate random parameters ---
        number_tasks_per_process = [[] for x in range(num_processes + 1)] # length of each process as int
        sum_all_tasks_of_processes = 0
        for p in range(num_processes):
             number_tasks = randint(min_len_process, max_len_process)
             number_tasks_per_process[p] = number_tasks
             sum_all_tasks_of_processes += number_tasks

        num_free_time_tasks = int(sum_all_tasks_of_processes / 100 * free_time)
        number_tasks_per_process[-1] = num_free_time_tasks

        # generating actual tasks per process
        tasks_per_process = Plan.generate_tasks_for_processes(number_tasks_per_process, min_len_task, max_len_task)

        tasks_for_plan = Plan.generate_realistic_plan(tasks_per_process)
        buffer_list = Plan.generate_buffer_list(tasks_per_process, (min_buffer, max_buffer))

        deadline_list = Plan.generate_deadlines(tasks_for_plan, buffer_list)
        processes = []
        # create process instances
        for i in range(num_processes):
            processes.append(Process(tasks_per_process[i], buffer_list[i], deadline_list[i]))

        assert len(deadline_list) == len(buffer_list)
        assert sum_all_tasks_of_processes + num_free_time_tasks == len(tasks_for_plan)

        plan = Plan(tasks_for_plan, processes)

        if file_path is not None:
            with open(file_path, 'w') as f:
                for t in plan:
                    f.write(str(t)+'\n')

        print(f'plan with {len(plan)} tasks created')
        return plan


    @staticmethod
    def generate_realistic_plan(processes: List[List[Task]]) -> List[Task]:
        """
        Mixes up the plan in such a way that there is some kind of meaningful switching between tasks for different processes/jobs. The Task-List on the last index is for free slots

        :param processes: List of List of Tasks, that represent processes
        :return: List of Tasks that switches as much as possible between Tasks
        """

        def sum_rec(l):
            if len(l) == 1:
                return len(l[0])
            else:
                return len(l[0]) + sum_rec(l[1:])

        ps = deepcopy(processes)

        sum_tasks = sum_rec(ps)
        num_processes = len(ps)
        plan = []
        last_picked = None
        next_pick = None

        for i in range(sum_tasks):
            available_processes = set(range(num_processes)) - set([last_picked])
            if len(available_processes) == 0:
                available_processes = {0}
            p_to_pick = choice(tuple(available_processes))

            cur_process = ps[p_to_pick]
            plan.append(cur_process[0])
            ps[p_to_pick] = ps[p_to_pick][1:]
            if len(ps[p_to_pick]) == 0:
                del ps[p_to_pick]
                num_processes -= 1
            last_picked = p_to_pick

        assert len(ps) == 0

        return plan


    @staticmethod
    def generate_buffer_list(process_task_list, min_max) -> [int]:
        """
        : param process_task_list: [[task0_p0, task1_p0,...],]
        : param min_max: tuple(min_buffer, max_buffer)
        : return: List of buffer-sizes per process
        """
        buffers = []
        buffer_percentage = randint(min_max[0], min_max[1])/100
        for i, process in enumerate(process_task_list):
            if i == len(process_task_list) -1:
                continue
            length_all = sum(process)
            buffers.append(length_all * buffer_percentage)

        return buffers

    @staticmethod
    def generate_deadlines(plan_task_list, buffer_list):
        """
        : param plan_task_list: [task0, task1, task2,...]
        : param buffer_list: [int, int, int,...]
        """
        processes_in_plan = set()
        for task in plan_task_list:
            if task.process_id not in processes_in_plan:
                processes_in_plan = processes_in_plan.union({task.process_id})
        processes_in_plan = list(processes_in_plan - {-1})

        deadlines = [0 for x in range(len(processes_in_plan))]
        time = 0

        for task in plan_task_list:
            time += task.length_plan
            if task.process_id != -1:
                deadlines[task.process_id] = time


        for i in range(len(buffer_list)):
            deadlines[i] += buffer_list[i]

        return deadlines



    @staticmethod
    def find_last_task_ending(plan: List[Task], num_processes: int) -> List[int]:
        """
        Returns the finishing time for each process
        """
        instr_counter = 0
        # holds finishing time for latest task of each process
        latest_task = [[] for x in range(num_processes)]
        for task in plan:
            instr_counter += task.length_plan
            if task.task_id == -1:
                continue
            latest_task[task.process_id] = instr_counter
        return latest_task

    @staticmethod
    def generate_tasks_for_processes(length_per_process: List[int], min_len, max_len):
        """
        : length_per_process : Number of tasks per process, last process are free_slots
        : min/max_len: length of tasks to be generated
        return: [[task0_p0, task1_p0],[task0_p1, task1_p1],...[task0_p-1, task1_p-1,...]]
        """
        task_id = 0
        process_id = 0
        tasks_per_process = []
        for process_id, number_tasks_per_process in enumerate(length_per_process):
            cur_task_list = []
            if process_id == len(length_per_process) -1:
                process_id = -1

            for new_task in range(number_tasks_per_process):
                length_plan = randint(min_len, max_len)
                new_task = Task(length_plan, process_id, task_id)
                cur_task_list.append(new_task)
                task_id += 1

            tasks_per_process.append(cur_task_list)


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
    def sort_plan(tasks: List['Task']) -> list:
        """
        Sorts all tasks of a long list of task into a list for each process.
        Input: [task0,task1,task2,...]
        Output:[[task0, task2], [task1,...],...] where the index is the process id
        """
        # first count number of different processes
        all_ps = {}
        for task in tasks:
            if task.process_id not in all_ps:
                all_ps.union({task.process_id})

        num_processes = len(all_ps)

        task_lists = [[] for p in range(num_processes)]
        for t in p.task_list:
            if t.process_id == -1:
                continue
            else:
                task_lists[t.process_id].append(t)
        return task_lists

    @staticmethod
    def read_plan_from_file(path) -> "Plan":
        """
        Reads the plan pointed to by the string in path
        """
        # List of tasks of all processes
        task_list = []
        # Tuples with (buffer, deadline)
        process_list = []
        process_info = []

        def back_together(lists): return "".join(lists)

        with open(path, 'r') as p:
            all = p.readline()
            num_processes = int(all.split(';')[0])
            print(f'number processes: {num_processes}')
            process_data = all.split(';;;')[0].split(';')[1:]
            print(process_data)
            all = back_together(all.split(";;;")[1])
            # process information
            for p in range(num_processes):
                p_info = process_data[p]
                buffer = p_info.split(',')[2]
                deadline = p_info.split(',')[3]
                process_info.append((buffer, deadline))
                print(f'process {p}: buffer = {buffer}, deadline = {deadline}')

            # task information
            task_strings = all.split(';')
            task_strings.remove('\n')
            for t in task_strings:
                parts = t.split(',')
                parts = list(map(int, parts))
                process_id = parts[1]
                task_id = parts[2]
                length_plan = parts[3]
                length_real = parts[4]
                new_t = Task(length_plan, process_id, task_id, length_real=length_real)
                task_list.append(new_t)
                print(task_id)

            tasks_per_p = Plan.sort_plan(task_list, num_processes)

            for p in process_list:
                p_info = process_info[0]
                process_info = process_info[1:]
                process_list.append(Process(tasks_per_p[0], p_info[0], p_info[1]))

            read_plan = Plan(task_list, process_list)
            return read_plan
