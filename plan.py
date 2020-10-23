import numpy as np
from random import randint
from copy import deepcopy

sigma = None

class Task:
    def __init__(self, length, process_id, task_id):
        global sigma
        self.length_plan = int(length) # instructions left to process
        self.length_real = int(np.random.normal(length, length/100*sigma, 1))
        self.process_id = process_id
        self.task_id = task_id
        self.late = False
        self.task_finished = False

    def run(self, ins) -> int:
        '''
        Runs the task, returns 1 if the task hasn't finished and -n if it has finished.
        n is the amount of instructions that are left in the current tick
        '''
        self.length_real -= ins
        self.length_plan -= ins
        return self.length_real if self.length_real < 0  else 1

    def __str__(self):
        return f'(process: {self.process_id}, id: {self.task_id}, plan_len: {self.length_plan}, real_len:{self.length_real})'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return self.length_plan + other.length_plan

    def __radd__(self, other):
        return other + self.length_plan


class Plan:
    def __init__(self, processes, task_list):
        self.process_info = processes # list of tuples [(task_list_p0, buffer_p0),(task_list_p1, buffer_p1),...]
        self.task_list = task_list # [task0,]

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

        # create tasks for each process
        tasks_per_process = [[] for x in range(num_processes)] # [[taks0 of p0, task1 of p0],[task2 of p1]...]
        cur_id = 0
        for cur_process in range(num_processes):
            for i in range(process_length[cur_process]):
                tasks_per_process[cur_process].append(Task(randint(min_len_task,max_len_task), cur_process, cur_id))
                cur_id += 1

        # create plan out of tasks for each process
        plan = []
        sum_tasks = 0
        for p in tasks_per_process:
            sum_tasks += len(p)

        all_pro_and_tasks = deepcopy(tasks_per_process)

        # generate plan for whole node as one list
        cur_id = 0
        for task_id in range(sum_tasks):
            new_task = None
            while new_task is None:
                process_to_pick_from = randint(0, num_processes-1)
                try:
                    new_task = all_pro_and_tasks[process_to_pick_from].pop()
                except IndexError:
                    all_pro_and_tasks.remove([])
                    num_processes -= 1
            new_task.id = cur_id
            plan.append(new_task)
            cur_id += 1
        plan.sort(key=id)

        # add free time slots
        free_slots = 0
        for i in range(sum_tasks):
             length = sum_tasks
             if randint(0,100) < free_time:
                plan.insert(randint(0, length), Task(randint(min_len_task, max_len_task),-1, None))
                length += 1
                free_slots += 1

        # calc buffers
        buffer_list = []
        for p in tasks_per_process:
            sum_instructions = 0
            for t in p:
                sum_instructions += t.length_plan
            buffer_list.append(sum_instructions*(randint(min_buffer,max_buffer)/100))
        # create plan data types
        processes = []
        for i in range(len(process_length)):
            processes.append((tasks_per_process[i], buffer_list[i]))

        assert len(processes) == len(process_length)
        assert len(plan) == sum_tasks + free_slots

        if file_path is not None:
            with open(file_path, 'w') as f:
                for t in plan:
                    f.write(str(t)+'\n')
        print(f'plan with {len(plan)} tasks created')
        return Plan(processes, plan)


    @staticmethod
    def pick_next_task(all_pro_and_tasks):
        return all_pro_and_tasks[process_to_pick].pop()
