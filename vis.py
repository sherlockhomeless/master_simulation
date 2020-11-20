#!/usr/bin/env python3

from os import listdir
import matplotlib.pyplot as plt

from sim import IPS

"""
Thrshold logging done in files of format thresh_[PROCESS_ID].log
Format: [P_ID] [T1] [T2] [T3]
"""

#  ---file names---

LOG_FOLDER = "logs" # Base-Folder for all log-files
PIC_FOLDER = "pics" # Base-Folder for graphics
THRESH2_ALL = 'thresh2_all.log' # all t2 logs of all processes
THRESH_CHRON = 'thresh_cron.log' # chronological change of t1, t2, mt2



def run_vis():

    # visualize threshold development for all processes
    log_files = find_threshold_logs("thresh")
    thresholds = parse_logs(log_files)
    statistics = do_stat(thresholds)
    vis_all_processes(thresholds)
    vis_all_processes(thresholds, thresh_type='t1')

    # visualize pure overreach allowed per process & threshold
    log_files = find_threshold_logs("pure")
    thresholds = parse_logs(log_files)
    vis_all_processes(thresholds, value_type='pure')
    vis_all_processes(thresholds, thresh_type='t1', value_type='pure')

def vis_all_processes(threshs, thresh_type='t2', value_type='sum'):
    """
    Visualize the development of Threshold 2 for all processes
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
        print(f'ploting graph {i}')
        plt.plot(t, t2, label = f'process {i}')


    # Setting the figure size
    plt.xlabel = 't'
    plt.ylabel = 'ips'
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
    print(logs)
    return logs

class log_struct:
    def __init__(self, taskid, t1, t2, mt2):
        self.task_id = taskid
        self.t1 = int(t1)/IPS
        self.t2 = int(t2)/IPS
        self.mt2 = int(mt2)/IPS


    def __str__(self) -> str:
        return f'[{self.t1}, {self.t2}, {self.mt2}]'

    def __repr__(self) -> str:
        return self.__str__()








if __name__ == '__main__':
    run_vis()
