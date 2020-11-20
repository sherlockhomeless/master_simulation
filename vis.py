#!/usr/bin/env python3

from os import listdir
import matplotlib.pyplot as plt

from sim import IPS

"""
Thrshold logging done in files of format thresh_[PROCESS_ID].log
Format: [P_ID] [T1] [T2] [T3]
"""

#  ---file names---

THRESH2_ALL = 'thresh2_all.log' # all t2 logs of all processes
THRESH_CHRON = 'thresh_cron.log' # chronological change of t1, t2, mt2




def run_vis():
    log_files = find_threshold_logs()
    thresholds = parse_logs(log_files)
    statistics = do_stat(thresholds)
    visualize(thresholds)


def visualize(threshs):
    # todo: legend
    vis_all_processes()
    plt.clt() # should clear all axis


def vis_all_processes(threshs):
    t = list(range(max(len(i) for i in threshs)))
    functions = []

    for p in threshs:
        functions.append([])
        for new_t in p:
            functions[-1].append(new_t.t2)
        while len(functions[-1]) < len(t):
            functions[-1].append(0)

    for i, t2 in enumerate(functions):
        print(f'ploting graph {i}')
        plt.plot(t, t2, label = f'process {i}')


    # Setting the figure size
    plt.xlabel = 't'
    plt.ylabel = 'ips'
    plt.legend()
    save_fig(THRESH2_ALL)



def save_fig(fpath):
    plt.save_fig(fpath, dpi=150)


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


def find_threshold_logs() -> list:
    """
    find all threshold log files in cwd
    """
    files = listdir('.')
    logs = []
    for f in files:
        if "thresh_" in f and "log" in f:
            logs.append(f)
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
