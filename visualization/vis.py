#!/usr/bin/env python3
from os import listdir
from os.path import join
from typing import List
import matplotlib.pyplot as plt
import plan
from config import INS_PER_TICK

"""
Thrshold logging done in files of format thresh_[PROCESS_ID].log
Format: [P_ID] [T1] [T2] [T3]
"""

#  ---file names---
BASE_FOLDER = "/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation"
LOG_FOLDER = join(BASE_FOLDER, "logs")  # Base-Folder for all log-files
PIC_FOLDER = join(BASE_FOLDER, "pics")  # Base-Folder for graphics
THRESH2_ALL = 'thresh2_all.log' # all t2 logs of all processes
THRESH_CHRON = 'thresh_cron.log' # chronological change of t1, t2, mt2
PLAN = "plan.log"
visualize_plan = True


def vis():
    if visualize_plan:
        vis_plan()


def vis_plan():
    path_plan = join(LOG_FOLDER, PLAN)
    p = plan.Plan.read_plan_from_file(path_plan)
    print(p)



def run_vis():

    # visualize threshold development for all processes
    log_files = find_threshold_logs("thresh_")
    thresholds = parse_logs(log_files)
    statistics = do_stat(thresholds)
    vis_all_processes(thresholds)
    vis_all_processes(thresholds, thresh_type='t1')

    # visualize pure overreach allowed per process & threshold
    log_files = find_threshold_logs("pure")
    thresholds = parse_logs(log_files)
    vis_all_processes(thresholds, value_type='pure')
    vis_all_processes(thresholds, thresh_type='t1', value_type='pure')

    log_files = find_threshold_logs("per_tick_thresh_sum")
    thresholds = parse_logs(log_files)
    vis_chronological(thresholds[0])

    log_files = find_threshold_logs("per_tick_thresh_pure")
    thresholds = parse_logs(log_files)
    vis_chronological(thresholds[0], value_type='pure')

def vis_chronological(threshs: List["log_struct"], value_type='sum'):
    """
    Visualization of all thresholds per chronologically increasing tick. Threshs is a List of log_structs
    """
    t = list(range(len(threshs))) # gets time axes
    # --- fill lists with corresponding data ---
    graph_labels = ['t1', 't2']
    t1_all = []
    t2_all = []
    mt2_all = []
    last = None
    #set_trace()
    for thresh in threshs:
        if thresh.task_id == '-1':
            t1_all.append(t1_all[-1])
            t2_all.append(t2_all[-1])
            mt2_all.append(mt2_all[-1])
            continue
        t1_all.append(thresh.t1)
        t2_all.append(thresh.t2)
        mt2_all.append(thresh.mt2)

    # --- Plot ---
    for i, graph in enumerate((t1_all, t2_all)):
        plt.plot(t, graph, label=graph_labels[i])

    plt.xlabel = 't'
    plt.ylabel = 'INS_PER_TICK'
    plt.legend()
    print(f'ploting chronological threshold')
    save_fig(f"thresh_chrono_{value_type}")




def vis_all_processes(threshs, thresh_type='t2', value_type='sum'):
    """
    Visualize the development of Thresholds for all processes
    valuetype determines if visualization eather shows the threshold including the planed instructions (sum) or just the threshods
    """
    t = list(range(max(len(i) for i in threshs)))
    functions = []

    for p in threshs:
        functions.append([])
        for new_t in p:
            functions[-1].append(new_t.t2) if thresh_type == 't2' else functions[-1].append(new_t.t1)
        while len(functions[-1]) < len(t):
            functions[-1].append(0)

    for i, t2 in enumerate(functions):
        print(f'ploting graph {i} (t-type: {thresh_type}, value_type: {value_type})')
        plt.plot(t, t2, label = f'process {i}')


    # Setting the figure size
    plt.xlabel = 't'
    plt.ylabel = 'INS_PER_TICK'
    plt.legend()
    save_fig(f"all_processes_{thresh_type}_{value_type}")

def save_fig(filename):
    plt.savefig(f'{PIC_FOLDER}/{filename}.png', dpi=150)
    plt.clf() # should clear all axis



def do_stat(threshs) -> dict:
    stats = dict()
    for i,p in enumerate(threshs):
        minimum = min([x.t2 for x in p])
        stats[f'min_{i}'] = minimum
        maximum = max([x.t2 for x in p])
        stats[f'max_{i}'] = maximum

    print(stats)
    return stats

def parse_logs(log_files) -> list:
    """
    parse all logs into log_struct and return list of lists full of log_structs
    """
    logs = []
    for log in log_files:
        new_log = []
        with open(log, 'r') as f:
            for line in f:
                if line[0] == '#' or 'None' in line:
                    continue
                line = line.replace('\n', '')
                parts = line.split(' ')
                new_log.append(log_struct(parts[0], parts[1], parts[2], parts[3]))
        logs.append(new_log)
    return logs


def find_threshold_logs(pattern: str) -> list:
    """
    find all threshold log files in LOG_FOLDER that contains the given pattern
    """
    files = listdir(LOG_FOLDER)
    logs = []
    for f in files:
        if pattern in f and ".log" in f:
            logs.append(f'{LOG_FOLDER}/{f}')
    logs.sort()
    print(f'[FIND] Found logs {logs} for pattern {pattern}')
    return logs

class log_struct:
    def __init__(self, taskid, t1, t2, mt2):
        """
        Simple data structure that stores threshold information. Pure instructions are converted to a
        """
        self.task_id = taskid
        self.t1 = int(int(t1)/INS_PER_TICK)
        self.t2 = int(int(t2)/INS_PER_TICK)
        self.mt2 = int(int(mt2)/INS_PER_TICK)



    def __str__(self) -> str:
        return f'[{self.task_id}{self.t1}, {self.t2}, {self.mt2}]'

    def __repr__(self) -> str:
        return self.__str__()




if __name__ == '__main__':
    vis()
