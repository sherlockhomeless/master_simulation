from dataclasses import dataclass
from typing import List


class LogParser:
    def __init__(self, log_path):
        self.log_path = log_path
        log_f = open(log_path, 'r')
        self.lines_log = log_f.readlines()
        log_f.close()
        self.tick_events: List[TickEvent] = []

    def read_log(self):
        for line in self.lines_log:
            cur_tick = []
            split = line.split(';')
            try:
                for pair in split:
                    pair = pair.split(':')
                    name = pair[0]
                    val = int(float(pair[1]))
                    cur_tick.append((name, val))
            except ValueError as e:
                print("ERROR:" + str(e) + line)
            new_tick = TickEvent(*cur_tick)
            self.tick_events.append(new_tick)

    def get_parsed_logs(self) -> List["TickEvent"]:
        return self.tick_events


@dataclass
class TickEvent(dict):
    tick_counter: (str, int)
    t1: (str,  int)
    t1_pure: (str,  int)
    t2_task: (str,  int)
    t2_task_pure: (str,  int)
    t2_process_capacity: (str,  int)
    t2_process_plan: (str, int)
    t2_node: (str,  int)
    tm2_task_sum: (str,  int)
    tm2_task_pure: (str,  int)
    tm2_node: (str,  int)
    task_id: (str,  int)
    task_length_plan_unchanged: (str,  int)
    task_length_plan_remaining: (str,  int)
    task_length_real: (str,  int)
    lateness_task: (str,  int)
    preemptions: (str,  int)
    process_id: (str,  int)
    lateness_process: (str,  int)
    lateness_node: (str,  int)

    def __getitem__(self, item):
        items = vars(self)
        return items[item]






