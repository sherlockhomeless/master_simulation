#!/usr/bin/env python3

from os import listdir
import matplotlib.pyplot as plt

"""
Thrshold logging done in files of format thresh_[PROCESS_ID].log
Format: [P_ID] [T1] [T2] [T3]
"""


def run_vis():
    log_files = find_threshold_logs()
    thresholds = parse_logs(log_files)
    visualize(thresholds)

def visualize(threshs):
    # todo: legend
    plt.xlabel = 't'
    plt.ylabel = 'instructions'

    t = list(range(max(len(i) for i in threshs)))
    functions = []

    for p in threshs:
        functions.append([])
        for new_t in p:
            functions[-1].append(new_t.t2)
        while len(functions[-1]) < len(t):
            print("here")
            functions[-1].append(0)

    for i, t2 in enumerate(functions):
        print(f'ploting graph {i}')
        plt.plot(t, t2)

    plt.show()



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
                new_log.append(log_struct(parts[1], parts[2], parts[3]))
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
    return logs

class log_struct:
    def __init__(self, t1, t2, mt2):
        self.t1 = int(t1)
        self.t2 = int(t2)
        self.mt2 = int(mt2)

    def __str__(self) -> str:
        return f'[{self.t1}, {self.t2}, {self.mt2}]'

    def __repr__(self) -> str:
        return self.__str__()








if __name__ == '__main__':
    run_vis()
